"""
PricePing Trending Deals API Routes
===================================
Serves live verified deals across Amazon, Flipkart, Myntra, AJIO, and Nykaa.
Never relies on the frontend to decide whether a deal is real.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import logging

from db.database import get_db
from schemas.schemas import TrendingDealsResponse
from services.trending_engine import TrendingEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trending-deals", tags=["Trending Deals"])


@router.get("", response_model=TrendingDealsResponse)
async def get_trending_deals(
    store: Optional[str] = Query(None, description="Filter by store: all, amazon, flipkart, myntra, ajio, nykaa"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
):
    """
    Step 15: Retrieve live verified trending deals across all 5 stores.
    Responds from Redis cache in milliseconds without blocking on store scraping.
    """
    return TrendingEngine.get_trending_deals(
        db=db,
        store_filter=store,
        category_filter=category,
    )


@router.post("/refresh")
async def refresh_trending_deals(
    db: Session = Depends(get_db),
):
    """
    Background or admin trigger to immediately re-evaluate deals and update cache.
    """
    deals = TrendingEngine.refresh_trending_deals(db=db)
    return {
        "success": True,
        "message": f"Successfully validated and refreshed {len(deals)} trending deals across all 5 stores.",
        "total_deals": len(deals),
    }
