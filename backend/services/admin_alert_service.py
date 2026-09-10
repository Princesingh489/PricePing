import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from core.config import settings

logger = logging.getLogger(__name__)

# Cooldown tracking to prevent alert spam: key -> timestamp
_ALERT_COOLDOWN: Dict[str, datetime] = {}
COOLDOWN_HOURS = 6

# In-memory incident log for the Admin Console UI (keeps last 100 entries)
_INCIDENTS_LOG: List[Dict[str, Any]] = []
MAX_LOG_ENTRIES = 100


def record_incident(
    store: str,
    url: str,
    error_reason: str,
    product_name: str = "Unknown Product",
    severity: str = "WARNING",
    status: str = "OPEN",
) -> Dict[str, Any]:
    """Records an incident in the Admin incident log and triggers external alerts if needed."""
    incident = {
        "id": len(_INCIDENTS_LOG) + 1,
        "product_name": product_name or "Unknown Product",
        "store": store.upper() if store else "UNKNOWN",
        "url": url,
        "error_reason": error_reason,
        "severity": severity,
        "status": status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "timestamp_display": datetime.utcnow().strftime("%d %b %Y, %H:%M UTC"),
    }

    _INCIDENTS_LOG.insert(0, incident)
    if len(_INCIDENTS_LOG) > MAX_LOG_ENTRIES:
        _INCIDENTS_LOG.pop()

    return incident


def get_incident_logs(limit: int = 50) -> List[Dict[str, Any]]:
    """Returns the most recent scraper/URL failure events."""
    return _INCIDENTS_LOG[:limit]


def is_on_cooldown(alert_key: str) -> bool:
    """Checks if an alert for this key was sent within the cooldown window."""
    last_sent = _ALERT_COOLDOWN.get(alert_key)
    if not last_sent:
        return False
    if datetime.utcnow() - last_sent < timedelta(hours=COOLDOWN_HOURS):
        return True
    return False


def mark_sent(alert_key: str):
    """Marks alert as sent to enforce cooldown."""
    _ALERT_COOLDOWN[alert_key] = datetime.utcnow()


async def send_admin_alert(
    title: str,
    product_name: str,
    store: str,
    url: str,
    error_msg: str,
    failure_count: int = 1,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Dispatches notifications to WhatsApp, Telegram, and Email according to configuration.
    Enforces anti-spam cooldown unless force=True.
    """
    cooldown_key = f"{store}:{url}"
    if not force and is_on_cooldown(cooldown_key):
        logger.info(f"Skipping alert for {url} - within {COOLDOWN_HOURS}h cooldown window.")
        return {"status": "cooldown_skipped", "cooldown_hours": COOLDOWN_HOURS}

    # Record incident for Admin Console
    record_incident(store=store, url=url, error_reason=error_msg, product_name=product_name)

    results = {
        "whatsapp": False,
        "telegram": False,
        "email": False,
    }

    # Formatted Alert Message
    alert_text = (
        f"🚨 *[Price Ping Admin Alert]*\n\n"
        f"⚠️ *Issue:* {title}\n"
        f"📦 *Product:* {product_name}\n"
        f"🏬 *Store:* {store.upper()}\n"
        f"🔗 *URL:* {url}\n"
        f"❌ *Error:* {error_msg}\n"
        f"🔄 *Failed Checks:* {failure_count}\n"
        f"🕒 *Time:* {datetime.utcnow().strftime('%d-%b-%Y %H:%M UTC')}\n\n"
        f"👉 *Admin Dashboard:* https://priceping.store/admin"
    )

    # 1. WhatsApp Alert via Twilio
    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.ADMIN_WHATSAPP_NUMBER:
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            target_wa = settings.ADMIN_WHATSAPP_NUMBER
            if not target_wa.startswith("whatsapp:"):
                target_wa = f"whatsapp:{target_wa}"

            from_wa = settings.TWILIO_WHATSAPP_FROM
            if not from_wa.startswith("whatsapp:"):
                from_wa = f"whatsapp:{from_wa}"

            client.messages.create(
                from_=from_wa,
                to=target_wa,
                body=alert_text,
            )
            results["whatsapp"] = True
            logger.info(f"WhatsApp alert sent successfully to {target_wa}")
        except Exception as wa_err:
            logger.error(f"WhatsApp alert dispatch failed: {wa_err}")
            results["whatsapp_error"] = str(wa_err)

    # 2. Telegram Bot Alert
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_ADMIN_CHAT_ID:
        try:
            import httpx
            tg_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": settings.TELEGRAM_ADMIN_CHAT_ID,
                "text": alert_text,
                "parse_mode": "Markdown",
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(tg_url, json=payload)
                if resp.status_code == 200:
                    results["telegram"] = True
                    logger.info("Telegram admin alert sent successfully.")
                else:
                    logger.warning(f"Telegram alert responded with {resp.status_code}: {resp.text}")
                    results["telegram_error"] = resp.text
        except Exception as tg_err:
            logger.error(f"Telegram alert dispatch failed: {tg_err}")
            results["telegram_error"] = str(tg_err)

    # 3. Email Alert Fallback
    if settings.SMTP_USER and settings.SMTP_PASSWORD and settings.FIRST_SUPERUSER_EMAIL:
        try:
            from services.notification_service import send_email_notification
            email_html = f"""
            <div style="font-family: sans-serif; max-width: 600px; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px;">
                <h2 style="color: #e11d48; margin-top: 0;">🚨 Price Ping Scraper Alert</h2>
                <p>A monitored product URL has failed automated checks or encountered a scraping error.</p>
                <table style="width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px;">
                    <tr><td style="padding: 6px; font-weight: bold;">Product:</td><td>{product_name}</td></tr>
                    <tr><td style="padding: 6px; font-weight: bold;">Store:</td><td>{store.upper()}</td></tr>
                    <tr><td style="padding: 6px; font-weight: bold;">URL:</td><td><a href="{url}">{url}</a></td></tr>
                    <tr><td style="padding: 6px; font-weight: bold;">Error:</td><td style="color: #dc2626;">{error_msg}</td></tr>
                    <tr><td style="padding: 6px; font-weight: bold;">Failed Checks:</td><td>{failure_count}</td></tr>
                </table>
                <p><a href="https://priceping.store/admin" style="background: #4f46e5; color: white; padding: 10px 18px; text-decoration: none; border-radius: 6px; display: inline-block;">Open Admin Panel</a></p>
            </div>
            """
            sent = send_email_notification(
                to_email=settings.FIRST_SUPERUSER_EMAIL,
                subject=f"🚨 [Price Ping] Scraper Failure on {store.upper()} - {product_name[:30]}",
                body_html=email_html,
            )
            results["email"] = sent
        except Exception as em_err:
            logger.error(f"Email admin alert failed: {em_err}")
            results["email_error"] = str(em_err)

    mark_sent(cooldown_key)
    return {
        "status": "dispatched",
        "results": results,
        "configured_channels": {
            "whatsapp": bool(settings.TWILIO_ACCOUNT_SID and settings.ADMIN_WHATSAPP_NUMBER),
            "telegram": bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_ADMIN_CHAT_ID),
            "email": bool(settings.SMTP_USER and settings.FIRST_SUPERUSER_EMAIL),
        }
    }
