"""
PriceWatch India - FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.config import settings
from db.database import engine, Base
from db import models  # noqa: ensures models are registered
from api.routes import auth, products, alerts, notifications, admin, trending

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    logger.info("Starting PriceWatch India API...")
    try:
        Base.metadata.create_all(bind=engine)
        # Safe non-destructive column additions for PostgreSQL & SQLite
        from sqlalchemy import text, inspect
        with engine.begin() as conn:
            inspector = inspect(engine)
            if engine.dialect.name == "postgresql":
                prod_cols = [c["name"] for c in inspector.get_columns("products")]
                for col_name, col_type in [
                    ("rating", "DOUBLE PRECISION"),
                    ("rating_count", "INTEGER"),
                    ("review_count", "INTEGER"),
                    ("currency", "VARCHAR DEFAULT 'INR'"),
                    ("original_price", "DOUBLE PRECISION"),
                    ("discount_percentage", "DOUBLE PRECISION"),
                    ("store", "VARCHAR"),
                    ("external_product_id", "VARCHAR"),
                    ("brand", "VARCHAR"),
                    ("model", "VARCHAR"),
                    ("variant", "VARCHAR"),
                    ("images_json", "TEXT"),
                    ("colors_json", "TEXT"),
                    ("status", "VARCHAR(50) DEFAULT 'PENDING'"),
                    ("canonical_id", "VARCHAR"),
                    ("canonical_url", "TEXT"),
                    ("title", "VARCHAR(500)"),
                    ("image_url", "TEXT"),
                    ("average_price", "DOUBLE PRECISION"),
                    ("history_state", "VARCHAR(50) DEFAULT 'ORGANIC_COLD_START'"),
                    ("variants_json", "TEXT"),
                    ("observed_at", "TIMESTAMP"),
                    ("updated_at", "TIMESTAMP"),
                ]:
                    if col_name not in prod_cols:
                        conn.execute(text(f"ALTER TABLE products ADD COLUMN {col_name} {col_type};"))

                hist_cols = [c["name"] for c in inspector.get_columns("price_history")]
                for col_name, col_type in [
                    ("store", "VARCHAR"),
                    ("external_product_id", "VARCHAR"),
                    ("currency", "VARCHAR DEFAULT 'INR'"),
                    ("seller", "VARCHAR"),
                    ("source", "VARCHAR DEFAULT 'priceping_observation'"),
                    ("verified", "BOOLEAN DEFAULT TRUE"),
                    ("is_backfilled", "BOOLEAN DEFAULT FALSE"),
                    ("recorded_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                ]:
                    if col_name not in hist_cols:
                        conn.execute(text(f"ALTER TABLE price_history ADD COLUMN {col_name} {col_type};"))

                offer_cols = [c["name"] for c in inspector.get_columns("product_offers")]
                for col_name, col_type in [
                    ("match_confidence", "DOUBLE PRECISION"),
                    ("match_signals_json", "TEXT"),
                    ("match_reason", "VARCHAR"),
                    ("variants_json", "TEXT"),
                    ("observed_at", "TIMESTAMP"),
                ]:
                    if col_name not in offer_cols:
                        conn.execute(text(f"ALTER TABLE product_offers ADD COLUMN {col_name} {col_type};"))
            elif engine.dialect.name == "sqlite":
                inspector = inspect(engine)
                # Products table columns
                prod_cols = [c["name"] for c in inspector.get_columns("products")]
                for col_name, col_type in [
                    ("store", "VARCHAR"),
                    ("external_product_id", "VARCHAR"),
                    ("brand", "VARCHAR"),
                    ("model", "VARCHAR"),
                    ("variant", "VARCHAR"),
                    ("variants_json", "TEXT"),
                    ("images_json", "TEXT"),
                    ("colors_json", "TEXT"),
                    ("status", "VARCHAR DEFAULT 'PENDING'"),
                    ("canonical_id", "VARCHAR"),
                    ("canonical_url", "TEXT"),
                    ("title", "VARCHAR"),
                    ("image_url", "TEXT"),
                    ("average_price", "REAL"),
                    ("history_state", "VARCHAR DEFAULT 'ORGANIC_COLD_START'"),
                    ("observed_at", "DATETIME"),
                    ("updated_at", "DATETIME"),
                ]:
                    if col_name not in prod_cols:
                        conn.execute(text(f"ALTER TABLE products ADD COLUMN {col_name} {col_type};"))

                # Price history table columns
                hist_cols = [c["name"] for c in inspector.get_columns("price_history")]
                for col_name, col_type in [
                    ("store", "VARCHAR"),
                    ("external_product_id", "VARCHAR"),
                    ("currency", "VARCHAR DEFAULT 'INR'"),
                    ("seller", "VARCHAR"),
                    ("source", "VARCHAR DEFAULT 'priceping_observation'"),
                    ("verified", "BOOLEAN DEFAULT 1"),
                    ("is_backfilled", "BOOLEAN DEFAULT 0"),
                    ("recorded_at", "DATETIME"),
                ]:
                    if col_name not in hist_cols:
                        conn.execute(text(f"ALTER TABLE price_history ADD COLUMN {col_name} {col_type};"))

                # Product offers table columns
                offer_cols = [c["name"] for c in inspector.get_columns("product_offers")]
                for col_name, col_type in [
                    ("match_confidence", "REAL"),
                    ("match_signals_json", "TEXT"),
                    ("match_reason", "VARCHAR"),
                    ("variants_json", "TEXT"),
                    ("observed_at", "DATETIME"),
                ]:
                    if col_name not in offer_cols:
                        conn.execute(text(f"ALTER TABLE product_offers ADD COLUMN {col_name} {col_type};"))
        logger.info("Database tables and columns verified.")

        # Create default admin user if not exists
        from db.database import SessionLocal
        from core.security import get_password_hash
        with SessionLocal() as db:
            admin_user = db.query(models.User).filter(
                models.User.email == settings.FIRST_SUPERUSER_EMAIL
            ).first()
            if not admin_user:
                admin_user = models.User(
                    name="Admin",
                    email=settings.FIRST_SUPERUSER_EMAIL,
                    password_hash=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                    is_admin=True,
                    is_active=True,
                )
                db.add(admin_user)
                db.commit()
                logger.info(f"Admin user created: {settings.FIRST_SUPERUSER_EMAIL}")
            else:
                admin_user.password_hash = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
                admin_user.is_active = True
                admin_user.is_admin = True
                db.commit()
                logger.info(f"Admin user password verified/synced: {settings.FIRST_SUPERUSER_EMAIL}")
        import asyncio
        async def periodic_price_monitor():
            while True:
                try:
                    await asyncio.sleep(60)
                    from worker.tasks import perform_check_all_prices
                    await asyncio.to_thread(perform_check_all_prices)
                except asyncio.CancelledError:
                    break
                except Exception as err:
                    logger.error(f"Periodic price monitor error: {err}")

        monitor_task = asyncio.create_task(periodic_price_monitor())
    except Exception as e:
        logger.error(f"Error during startup lifespan: {e}")

    yield

    if "monitor_task" in locals() and monitor_task:
        monitor_task.cancel()
    logger.info("Shutting down PriceWatch India API.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Smart Product Price Tracker & Alert System for Indian E-Commerce",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(products.tracking_router)
app.include_router(alerts.router)
app.include_router(notifications.router)
app.include_router(admin.router)
app.include_router(trending.router)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/")
async def root():
    return JSONResponse({"message": f"Welcome to {settings.APP_NAME} API", "docs": "/api/docs"})
