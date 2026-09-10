"""
Celery Background Tasks
=======================
Price tracking, alert evaluation, and notification dispatch.
"""

import logging
from datetime import datetime
from typing import Optional
from celery import shared_task
from worker.celery_app import celery_app
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db import models
from services.platform_fetcher import fetch_updated_price, simulate_price_change
from services.notification_service import send_price_alert

logger = logging.getLogger(__name__)


def get_db_session() -> Session:
    return SessionLocal()


def evaluate_alert(alert: models.PriceAlert, product: models.Product) -> tuple[bool, str]:
    """
    Check if an alert condition is met.
    Returns (condition_met: bool, description: str)

    Implements intelligent deduplication:
    - Tracks `is_in_range` state on the alert
    - Sends alert only on TRANSITION from False → True
    - Resets when price leaves range
    """
    current_price = product.current_price
    if current_price is None:
        return False, ""

    condition_met = False
    description = ""

    if alert.alert_type == models.AlertTypeEnum.below_price:
        if alert.target_price and current_price <= alert.target_price:
            condition_met = True
            description = f"Price dropped to ₹{current_price:,.0f} (target: below ₹{alert.target_price:,.0f})"

    elif alert.alert_type == models.AlertTypeEnum.price_range:
        if (alert.minimum_price and alert.maximum_price and
                alert.minimum_price <= current_price <= alert.maximum_price):
            condition_met = True
            description = f"Price is ₹{current_price:,.0f} (in range ₹{alert.minimum_price:,.0f} – ₹{alert.maximum_price:,.0f})"

    elif alert.alert_type == models.AlertTypeEnum.percentage_drop:
        if alert.base_price and alert.percentage_drop:
            threshold_price = alert.base_price * (1 - alert.percentage_drop / 100)
            if current_price <= threshold_price:
                actual_drop = ((alert.base_price - current_price) / alert.base_price) * 100
                condition_met = True
                description = (f"Price dropped by {actual_drop:.1f}% to ₹{current_price:,.0f} "
                               f"(target: {alert.percentage_drop}% drop from ₹{alert.base_price:,.0f})")

    return condition_met, description


def perform_product_price_check(product_id: int):
    """Fetch the latest price for a single product and evaluate all active alerts."""
    db = get_db_session()
    try:
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            logger.warning(f"Product {product_id} not found")
            return

        # Check if product has any active trackers
        active_trackers = db.query(models.UserTrackedProduct).filter(
            models.UserTrackedProduct.product_id == product_id,
            models.UserTrackedProduct.tracking_status == models.TrackingStatusEnum.active
        ).count()

        if active_trackers == 0:
            return

        # Fetch updated price using high-accuracy scraper
        new_data = fetch_updated_price(product.product_url, product.platform)

        # Fail closed: Do not overwrite verified price if fetch failed or confidence is uncertain
        if not new_data or not new_data.success or new_data.current_price is None or (new_data.confidence_score and new_data.confidence_score < 70):
            err_msg = getattr(new_data, "error", None) or getattr(new_data, "error_message", None) or "Uncertain extraction confidence or bot check"
            logger.warning(f"Product {product_id} price fetch uncertain ({err_msg}). Keeping previous verified price.")
            try:
                from services.admin_alert_service import record_incident
                record_incident(
                    store=product.platform.value if hasattr(product.platform, "value") else str(product.platform),
                    url=product.product_url,
                    error_reason=err_msg,
                    product_name=product.product_name,
                    severity="WARNING",
                )
            except Exception:
                pass
            product.last_checked = datetime.utcnow()
            db.commit()
            return

        old_price = product.current_price
        new_price = new_data.current_price

        # False Price Spike Protection: If large unexpected jump, re-fetch once to verify
        from scrapers.validators import PriceValidator
        if old_price and PriceValidator.is_price_spike_suspicious(old_price, new_price):
            logger.info(f"Suspicious price change detected for Product {product_id} ({old_price} -> {new_price}). Re-verifying...")
            verify_data = fetch_updated_price(product.product_url, product.platform)
            if verify_data and verify_data.success and verify_data.current_price:
                new_price = verify_data.current_price
                new_data = verify_data
            else:
                logger.warning(f"Re-verification failed for Product {product_id}. Aborting update.")
                return

        # Update product
        product.current_price = new_price
        product.original_price = new_data.original_price or product.original_price
        product.discount_percentage = new_data.discount_percentage or product.discount_percentage
        product.availability = new_data.availability
        product.last_checked = datetime.utcnow()

        if product.lowest_price is None or new_price < product.lowest_price:
            product.lowest_price = new_price
        if product.highest_price is None or new_price > product.highest_price:
            product.highest_price = new_price

        # Deduplication Check: Do not insert identical records repeatedly
        store_str = (product.store or (product.platform.value if hasattr(product.platform, 'value') else str(product.platform))).lower()
        last_history = (
            db.query(models.PriceHistory)
            .filter(
                models.PriceHistory.product_id == product.id,
                models.PriceHistory.store == store_str,
            )
            .order_by(models.PriceHistory.checked_at.desc())
            .first()
        )

        now = datetime.utcnow()
        should_record = False
        if not last_history:
            should_record = True
        elif last_history.price != new_price:
            # Price changed - always record observation
            should_record = True
        elif (now - last_history.checked_at).total_seconds() >= 86400:
            # 24-hour periodic verification heartbeat
            should_record = True

        if should_record:
            history_entry = models.PriceHistory(
                product_id=product.id,
                store=store_str,
                external_product_id=product.external_product_id,
                price=new_price,
                original_price=new_data.original_price,
                currency=product.currency or "INR",
                availability=new_data.availability,
                seller=getattr(new_data, "seller", None),
                source="priceping_observation",
                verified=True,
                checked_at=now,
            )
            db.add(history_entry)
            db.commit()
            logger.info(f"Recorded genuine price observation for Product {product_id} at ₹{new_price}")
        else:
            db.commit()
            logger.info(f"Price unchanged (₹{new_price}) within 24h for Product {product_id}. Skipped duplicate record.")

        db.refresh(product)
        logger.info(f"Product {product_id} price verified & updated: {old_price} → {new_price}")

        # Evaluate alerts
        alerts = db.query(models.PriceAlert).filter(
            models.PriceAlert.product_id == product_id,
            models.PriceAlert.alert_status == models.AlertStatusEnum.active,
        ).all()

        for alert in alerts:
            condition_met, description = evaluate_alert(alert, product)

            if condition_met and not alert.is_in_range:
                # BUG-012 FIX: Add 24-hour cooldown to prevent spam notifications.
                # Without this, alerts re-trigger on every price check (every 60s) if price stays below target.
                cooldown_hours = 24
                if alert.last_triggered_at:
                    hours_since_trigger = (datetime.utcnow() - alert.last_triggered_at).total_seconds() / 3600
                    if hours_since_trigger < cooldown_hours:
                        logger.info(f"Alert {alert.id} cooldown active ({hours_since_trigger:.1f}h / {cooldown_hours}h). Skipping notification.")
                        # Still update is_in_range so the reset logic works
                        alert.is_in_range = True
                        db.commit()
                        continue

                # Transition from not-met to met → Send alert
                alert.is_in_range = True
                alert.last_triggered_at = datetime.utcnow()
                alert.last_triggered_price = new_price
                alert.alert_status = models.AlertStatusEnum.triggered
                db.commit()

                # Send notifications
                user = db.query(models.User).filter(models.User.id == alert.user_id).first()
                if user:
                    send_price_alert(db=db, alert=alert, product=product, user=user, alert_description=description)

                # Re-activate alert so it can trigger again if price leaves and re-enters
                alert.alert_status = models.AlertStatusEnum.active
                db.commit()

            elif not condition_met and alert.is_in_range:
                # Price left the range → Reset for next trigger
                alert.is_in_range = False
                db.commit()
                logger.info(f"Alert {alert.id} reset - price {new_price} left the target range")

    except Exception as exc:
        logger.error(f"Error checking price for product {product_id}: {exc}")
        db.rollback()
        raise exc
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def check_product_price(self, product_id: int):
    """Celery task wrapper for checking a single product price."""
    try:
        perform_product_price_check(product_id)
    except Exception as exc:
        raise self.retry(exc=exc)


def dispatch_price_check(product_id: int):
    """Dispatch price check task asynchronously without blocking or Redis connection errors."""
    import threading
    threading.Thread(target=perform_product_price_check, args=(product_id,), daemon=True).start()



def perform_check_all_prices():
    """Check prices for all actively tracked products."""
    db = get_db_session()
    try:
        active_product_ids = (
            db.query(models.UserTrackedProduct.product_id)
            .filter(models.UserTrackedProduct.tracking_status == models.TrackingStatusEnum.active)
            .distinct()
            .all()
        )
        product_ids = [row[0] for row in active_product_ids]
        logger.info(f"Running price checks for {len(product_ids)} products")
        for pid in product_ids:
            try:
                check_product_price.apply_async(args=[pid], countdown=0)
            except Exception:
                perform_product_price_check(pid)
        return {"checked": len(product_ids)}
    except Exception as e:
        logger.error(f"perform_check_all_prices failed: {e}")
        raise
    finally:
        db.close()


@celery_app.task
def check_all_prices():
    """Periodic Celery task: check prices for all actively tracked products."""
    return perform_check_all_prices()


# =========================================================================
# Overhauled Scraper Worker Task: Ultra-Fast Non-Blocking Pipeline
# =========================================================================

async def _execute_fast_scrape(canonical_url: str, target_variant_id: Optional[str] = None):
    """
    Executes high-speed scraping using Playwright route optimizer and JSON state extraction.
    Falls back to multi-tier extractor if direct React hydration is absent.
    """
    from playwright.async_api import async_playwright
    from scrapers.playwright_optimizer import create_optimized_page
    from scrapers.extractors.json_state_extractor import extract_react_state_from_html
    from services.platform_fetcher import async_fetch_product_data

    html_content = None
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-setuid-sandbox",
                    "--disable-gpu",
                    "--blink-settings=imagesEnabled=false",
                ]
            )
            try:
                page = await create_optimized_page(browser)
                logger.info(f"Navigating to {canonical_url} with optimized Playwright page...")
                await page.goto(canonical_url, wait_until="domcontentloaded", timeout=15000)
                html_content = await page.content()
            finally:
                await browser.close()
    except Exception as e:
        logger.warning(f"Playwright navigation failed for {canonical_url}: {e}")

    # 1. Try JSON state extractor if HTML was retrieved
    if html_content:
        try:
            return extract_react_state_from_html(html_content, target_variant_id)
        except Exception as e:
            logger.info(f"JSON state extractor did not find React state: {e}. Falling back to standard adapter...")

    # 2. Resilient fallback to platform fetcher
    fetch_result = await async_fetch_product_data(canonical_url)
    if fetch_result and fetch_result.success and fetch_result.current_price:
        from scrapers.extractors.json_state_extractor import ExtractedVariantData
        return ExtractedVariantData(
            title=fetch_result.product_name or "Tracked Product",
            price=fetch_result.current_price,
            original_price=fetch_result.original_price,
            image_url=fetch_result.product_image,
            size=getattr(fetch_result, "variant", None),
            is_in_stock=fetch_result.availability == models.AvailabilityEnum.in_stock,
            variant_id=target_variant_id or fetch_result.store_product_id,
            raw_state_found=False
        )

    raise ValueError(f"Could not reliably extract verified price and product details for {canonical_url}")


@celery_app.task(bind=True, name="worker.tasks.ingest_product_pipeline", max_retries=3, default_retry_delay=10)
def ingest_product_pipeline(self, product_id: int, canonical_url: str, platform: str, canonical_id: str):
    """
    Celery Background Ingest Pipeline:
    Step 1: Attempt 2-Year History Backfill (AGGREGATED_2YR vs ORGANIC_COLD_START).
    Step 2: Live Variant Scrape via Playwright with aggressive route interception.
    Step 3: Save today's live price (is_backfilled=False).
    Step 4: Recalculate metrics (lowest, highest, 90-day average).
    Step 5: Finalize Product record with status='ACTIVE'.
    """
    import asyncio
    db: Session = get_db_session()
    logger.info(f"Starting ingest_product_pipeline for Product {product_id} ({platform}:{canonical_id})")

    try:
        from services.history_fetcher import HistoricalAggregatorService
        from db.db_ops import bulk_insert_history, recalculate_product_metrics

        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            logger.error(f"Product {product_id} not found in database.")
            return

        # ----------------------------------------------------
        # Step 1: Attempt 2-Year History Backfill
        # ----------------------------------------------------
        try:
            hist_points = asyncio.run(HistoricalAggregatorService.fetch_history(platform, canonical_url, canonical_id))
        except Exception as e:
            logger.warning(f"History fetch error for Product {product_id}: {e}")
            hist_points = []

        if hist_points and len(hist_points) > 0:
            asyncio.run(bulk_insert_history(db, product_id, hist_points, is_backfilled=True, store=platform))
            product.history_state = "AGGREGATED_2YR"
            logger.info(f"Product {product_id}: Backfilled {len(hist_points)} historical points (AGGREGATED_2YR).")
        else:
            product.history_state = "ORGANIC_COLD_START"
            logger.info(f"Product {product_id}: Historical data unindexed; marked as ORGANIC_COLD_START.")

        db.commit()

        # ----------------------------------------------------
        # Step 2: Live Variant Scrape (High Speed Intercepted Playwright)
        # ----------------------------------------------------
        variant_id = canonical_id
        live_data = None
        try:
            live_data = asyncio.run(_execute_fast_scrape(canonical_url, variant_id))
        except Exception as scrape_err:
            logger.warning(f"Live scrape failed for {canonical_url}: {scrape_err}")

        # ----------------------------------------------------
        # Step 3: Save Today's Current Price
        # ----------------------------------------------------
        now = datetime.utcnow()
        if live_data and live_data.price:
            title_val = live_data.title or product.product_name or product.title
            product.product_name = title_val
            product.title = title_val
            product.current_price = live_data.price
            if live_data.original_price:
                product.original_price = live_data.original_price
                if live_data.original_price > live_data.price:
                    product.discount_percentage = round(
                        ((live_data.original_price - live_data.price) / live_data.original_price) * 100, 1
                    )
            if live_data.image_url:
                product.product_image = live_data.image_url
                product.image_url = live_data.image_url
            if live_data.size:
                product.variant = live_data.size

            product.availability = (
                models.AvailabilityEnum.in_stock if live_data.is_in_stock else models.AvailabilityEnum.out_of_stock
            )

            # Insert today's live price observation (is_backfilled=False)
            asyncio.run(bulk_insert_history(
                db,
                product_id,
                [{"recorded_at": now, "price": live_data.price, "original_price": live_data.original_price}],
                is_backfilled=False,
                store=platform
            ))

        # ----------------------------------------------------
        # Step 4: Analytics (Recalculate lowest, highest, 90-day avg)
        # ----------------------------------------------------
        asyncio.run(recalculate_product_metrics(db, product_id))

        # ----------------------------------------------------
        # Step 5: Finalize Product Status
        # ----------------------------------------------------
        product.canonical_id = canonical_id
        product.canonical_url = canonical_url
        product.status = "ACTIVE"
        product.last_checked = now
        product.updated_at = now
        db.commit()
        db.refresh(product)

        logger.info(f"Finalized ingestion for Product {product_id}: status=ACTIVE, state={product.history_state}")

    except Exception as exc:
        db.rollback()
        logger.warning(f"Error in ingest_product_pipeline for Product {product_id}: {exc}")
        if self.request.retries >= self.max_retries:
            product = db.query(models.Product).filter(models.Product.id == product_id).first()
            if product:
                product.status = "FAILED"
                product.updated_at = datetime.utcnow()
                db.commit()
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, name="worker.tasks.scrape_and_update_product", max_retries=3, default_retry_delay=10)
def scrape_and_update_product_task(self, product_id: int, canonical_url: str, target_variant_id: Optional[str] = None):
    """
    Wrapper calling ingest_product_pipeline for unified ingestion and backward compatibility.
    """
    db = get_db_session()
    try:
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        platform_val = product.store or (product.platform.value if hasattr(product.platform, 'value') else str(product.platform)) if product else "unknown"
        canonical_id = target_variant_id or (product.external_product_id if product else None) or ""
    finally:
        db.close()

    return ingest_product_pipeline(product_id, canonical_url, platform_val, canonical_id)


@celery_app.task(name="worker.tasks.refresh_trending_deals_task")
def refresh_trending_deals_task():
    """
    Periodic Celery Task: Re-evaluates trending deals across Amazon, Flipkart, Myntra, AJIO, and Nykaa.
    Validates prices, verifies images and availability, ranks top 20 deals, and refreshes cache.
    """
    db = get_db_session()
    try:
        from services.trending_engine import TrendingEngine
        logger.info("Executing periodic refresh_trending_deals_task...")
        deals = TrendingEngine.refresh_trending_deals(db)
        logger.info(f"Successfully refreshed {len(deals)} trending deals across all 5 stores.")
        return len(deals)
    except Exception as exc:
        logger.error(f"Error in refresh_trending_deals_task: {exc}")
        return 0
    finally:
        db.close()


