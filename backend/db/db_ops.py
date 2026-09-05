"""
High-Speed Bulk Database Operations for Price History & Analytics
==================================================================
Optimized PostgreSQL bulk operations using ON CONFLICT DO NOTHING for ultra-fast time-series ingestion
and analytical metric recalculations (all-time lowest, highest, 90-day average).
Supports both asynchronous (AsyncSession) and synchronous (Session) SQLAlchemy sessions.
"""

from __future__ import annotations
import inspect
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Union
from sqlalchemy import select, func, update, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from db import models

logger = logging.getLogger(__name__)


def _is_async(session: Any) -> bool:
    """Detects whether a session is an AsyncSession."""
    return isinstance(session, AsyncSession) or hasattr(session, "run_sync")


async def _execute(session: Any, stmt: Any):
    """Executes a statement handling both async and sync sessions."""
    if _is_async(session):
        return await session.execute(stmt)
    else:
        return session.execute(stmt)


async def _commit(session: Any):
    """Commits handling both async and sync sessions."""
    if _is_async(session):
        await session.commit()
    else:
        session.commit()


async def bulk_insert_history(
    session: Union[AsyncSession, Session],
    product_id: int,
    points: List[Dict[str, Any]],
    is_backfilled: bool = True,
    store: Optional[str] = None
) -> int:
    """
    High-speed bulk insertion of historical price records.
    Uses PostgreSQL INSERT ... ON CONFLICT (product_id, recorded_at) DO NOTHING
    to ingest hundreds of records in a single database round-trip (~20ms).
    """
    if not points:
        return 0

    # Ensure timezone-aware / uniform datetime objects
    rows = []
    now = datetime.utcnow()
    for pt in points:
        rec_at = pt.get("recorded_at")
        price = pt.get("price")
        if price is None or price <= 0 or not rec_at:
            continue

        # Strip timezone offset to keep database timestamps uniform UTC
        if isinstance(rec_at, datetime) and rec_at.tzinfo is not None:
            rec_at = rec_at.astimezone(timezone.utc).replace(tzinfo=None)

        rows.append({
            "product_id": product_id,
            "store": store,
            "price": float(price),
            "original_price": pt.get("original_price"),
            "currency": pt.get("currency", "INR"),
            "availability": models.AvailabilityEnum.in_stock,
            "source": "aggregated_history" if is_backfilled else "priceping_observation",
            "verified": True,
            "is_backfilled": is_backfilled,
            "recorded_at": rec_at,
            "checked_at": rec_at,
        })

    if not rows:
        return 0

    # Determine database dialect
    bind = session.bind if hasattr(session, "bind") and session.bind else None
    dialect_name = bind.dialect.name if bind else "postgresql"

    inserted_count = 0

    try:
        if dialect_name == "postgresql":
            # PostgreSQL upsert using ON CONFLICT DO NOTHING
            stmt = pg_insert(models.PriceHistory).values(rows)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["product_id", "recorded_at"]
            )
            result = await _execute(session, stmt)
            await _commit(session)
            inserted_count = result.rowcount if hasattr(result, "rowcount") else len(rows)

        elif dialect_name == "sqlite":
            # SQLite upsert
            stmt = sqlite_insert(models.PriceHistory).values(rows)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["product_id", "recorded_at"]
            )
            result = await _execute(session, stmt)
            await _commit(session)
            inserted_count = len(rows)

        else:
            # Fallback for generic SQL databases
            for r in rows:
                existing = await _execute(
                    session,
                    select(models.PriceHistory.id).where(
                        models.PriceHistory.product_id == product_id,
                        models.PriceHistory.recorded_at == r["recorded_at"]
                    )
                )
                if not existing.first():
                    obj = models.PriceHistory(**r)
                    if _is_async(session):
                        session.add(obj)
                    else:
                        session.add(obj)
                    inserted_count += 1
            await _commit(session)

        logger.info(f"Bulk inserted {len(rows)} history points for Product {product_id} (backfilled={is_backfilled}).")
        return inserted_count

    except Exception as exc:
        logger.warning(f"Error in bulk_insert_history for Product {product_id}: {exc}")
        # Fallback individual insert to prevent whole-batch drop
        for r in rows:
            try:
                obj = models.PriceHistory(**r)
                session.add(obj)
                await _commit(session)
                inserted_count += 1
            except Exception:
                if _is_async(session):
                    await session.rollback()
                else:
                    session.rollback()
        return inserted_count


async def recalculate_product_metrics(
    session: Union[AsyncSession, Session],
    product_id: int
) -> Dict[str, Optional[float]]:
    """
    Executes fast SQL aggregate queries to compute all-time lowest, highest,
    and 90-day average prices, updating the Product row accordingly.
    """
    now = datetime.utcnow()
    ninety_days_ago = now - timedelta(days=90)

    # 1. All-time MIN and MAX
    all_time_stmt = select(
        func.min(models.PriceHistory.price).label("min_price"),
        func.max(models.PriceHistory.price).label("max_price"),
        func.avg(models.PriceHistory.price).label("avg_price"),
    ).where(models.PriceHistory.product_id == product_id, models.PriceHistory.price > 0)

    all_res = await _execute(session, all_time_stmt)
    row = all_res.first()

    lowest = float(row[0]) if row and row[0] is not None else None
    highest = float(row[1]) if row and row[1] is not None else None
    overall_avg = float(row[2]) if row and row[2] is not None else None

    # 2. 90-day Average Price
    ninety_stmt = select(
        func.avg(models.PriceHistory.price).label("avg_90d")
    ).where(
        models.PriceHistory.product_id == product_id,
        models.PriceHistory.price > 0,
        models.PriceHistory.recorded_at >= ninety_days_ago
    )
    ninety_res = await _execute(session, ninety_stmt)
    ninety_row = ninety_res.first()

    avg_90d = float(ninety_row[0]) if ninety_row and ninety_row[0] is not None else overall_avg

    # Update Product row
    update_data = {
        "lowest_price": lowest,
        "highest_price": highest,
        "average_price": round(avg_90d, 2) if avg_90d is not None else None,
        "updated_at": now,
    }

    prod_update_stmt = (
        update(models.Product)
        .where(models.Product.id == product_id)
        .values(**update_data)
    )
    await _execute(session, prod_update_stmt)
    await _commit(session)

    logger.info(
        f"Recalculated metrics for Product {product_id}: "
        f"lowest=₹{lowest}, highest=₹{highest}, 90d_avg=₹{update_data['average_price']}"
    )

    return {
        "lowest_price": lowest,
        "highest_price": highest,
        "average_price": update_data["average_price"],
    }
