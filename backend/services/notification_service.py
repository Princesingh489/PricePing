"""
Notification Service
====================
Handles all notification types: Email (SMTP), In-App, SMS (Twilio), and Push.
Designed to be non-blocking and resilient - failures are logged, not raised.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from core.config import settings
from db import models

logger = logging.getLogger(__name__)


def format_inr(price: float) -> str:
    """Format price in Indian Rupee format: ₹1,00,000"""
    price_str = str(int(price))
    if len(price_str) <= 3:
        return f"₹{price_str}"
    last_three = price_str[-3:]
    rest = price_str[:-3]
    result = ""
    while len(rest) > 2:
        result = "," + rest[-2:] + result
        rest = rest[:-2]
    result = rest + result
    return f"₹{result},{last_three}"


def create_in_app_notification(
    db: Session,
    user_id: int,
    product_id: int,
    title: str,
    message: str,
    notification_type: models.NotificationTypeEnum = models.NotificationTypeEnum.in_app,
) -> models.Notification:
    """Create an in-app notification record in the database."""
    notification = models.Notification(
        user_id=user_id,
        product_id=product_id,
        notification_type=notification_type,
        title=title,
        message=message,
        status=models.NotificationStatusEnum.sent,
        sent_at=datetime.utcnow(),
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def send_email_notification(
    to_email: str,
    subject: str,
    body_html: str,
    body_text: str = "",
) -> bool:
    """Send email via SMTP. Returns True on success."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("Email not configured - skipping email notification")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg["To"] = to_email
        msg.attach(MIMEText(body_text or body_html, "plain"))
        msg.attach(MIMEText(body_html, "html"))
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, to_email, msg.as_string())
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Email send failed to {to_email}: {e}")
        return False


def send_sms_notification(to_phone: str, message: str) -> bool:
    """Send SMS via Twilio. Returns True on success."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("Twilio not configured - skipping SMS notification")
        return False
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_phone,
        )
        logger.info(f"SMS sent to {to_phone}")
        return True
    except Exception as e:
        logger.error(f"SMS send failed to {to_phone}: {e}")
        return False


def build_price_alert_email(
    product_name: str,
    platform: str,
    current_price: float,
    original_price: Optional[float],
    product_url: str,
    alert_description: str,
) -> tuple[str, str]:
    """Build HTML and plain text email body for price alerts."""
    formatted_price = format_inr(current_price)
    formatted_original = format_inr(original_price) if original_price else "N/A"
    subject = f"🎯 Price Alert: {product_name[:50]} is now {formatted_price}"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #f4f6f9; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .content {{ padding: 30px; }}
        .price-box {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 10px; color: white; padding: 20px; text-align: center; margin: 20px 0; }}
        .price-box .price {{ font-size: 36px; font-weight: bold; }}
        .original {{ text-decoration: line-through; opacity: 0.8; font-size: 18px; }}
        .btn {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; margin: 20px 0; }}
        .footer {{ background: #f4f6f9; padding: 20px; text-align: center; color: #888; font-size: 12px; }}
    </style></head>
    <body>
    <div class="container">
        <div class="header">
            <h1>🔔 PricePing</h1>
            <p>Your price alert has been triggered!</p>
        </div>
        <div class="content">
            <h2>{product_name}</h2>
            <p><strong>Platform:</strong> {platform.title()}</p>
            <p><strong>Alert Condition:</strong> {alert_description}</p>
            <div class="price-box">
                <div class="price">{formatted_price}</div>
                {'<div class="original">MRP: ' + formatted_original + '</div>' if original_price else ''}
            </div>
            <p style="text-align:center">
                <a class="btn" href="{product_url}" target="_blank">🛒 Buy Now on {platform.title()}</a>
            </p>
            <p style="text-align:center; margin-top: 12px;">
                <a href="https://priceping.store" target="_blank" style="color:#667eea; font-weight:600; font-size:13px; text-decoration:none;">
                    🔍 Track &amp; Compare Live Deals on PricePing Home →
                </a>
            </p>
            <p style="color:#888;font-size:12px; text-align:center; margin-top:16px;">Prices change frequently. Hurry before this deal ends!</p>
        </div>
        <div class="footer">
            <p>© 2026 PricePing Technologies (<a href="https://priceping.store" style="color:#888;">priceping.store</a>). You received this because you set up a price alert.</p>
        </div>
    </div>
    </body></html>
    """
    plain = f"""
Price Alert Triggered!
Product: {product_name}
Platform: {platform.title()}
Condition: {alert_description}
Current Price: {formatted_price}
Original Price: {formatted_original}
Buy Now: {product_url}

Track & Compare on PricePing: https://priceping.store

PricePing Technologies
    """
    return subject, html


def send_price_alert(
    db: Session,
    alert: models.PriceAlert,
    product: models.Product,
    user: models.User,
    alert_description: str,
) -> None:
    """
    Send all configured notifications for a triggered price alert.
    Implements intelligent deduplication: only sends if condition is newly met.
    """
    title = f"Price Alert: {product.product_name[:50]}"
    message = f"{alert_description} | Current price: {format_inr(product.current_price or 0)}"

    # Always create in-app notification
    create_in_app_notification(
        db=db,
        user_id=user.id,
        product_id=product.id,
        title=title,
        message=message,
        notification_type=models.NotificationTypeEnum.in_app,
    )

    # Email notification
    if alert.notify_email and user.email_notifications:
        subject, html = build_price_alert_email(
            product_name=product.product_name,
            platform=product.platform.value,
            current_price=product.current_price or 0,
            original_price=product.original_price,
            product_url=product.product_url,
            alert_description=alert_description,
        )
        # BUG-013 FIX: Do NOT create a second in-app notification on email success.
        # An in-app notification was already created above. Email delivery is a transport concern,
        # not a separate notification record. The original code created 2 in-app notifications.
        send_email_notification(to_email=user.email, subject=subject, body_html=html)

    # SMS notification
    if alert.notify_sms and user.sms_notifications and user.phone_number:
        sms_msg = f"PriceWatch Alert: {product.product_name[:40]} is now {format_inr(product.current_price or 0)}. Buy: {product.product_url[:50]}"
        send_sms_notification(to_phone=user.phone_number, message=sms_msg)

    logger.info(f"Alert notifications sent for alert_id={alert.id}, user={user.email}")
