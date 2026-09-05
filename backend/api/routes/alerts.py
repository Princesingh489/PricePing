from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from db.database import get_db
from db import models
from core.deps import get_current_user
from schemas.schemas import AlertCreate, AlertOut, AlertUpdate

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.post("", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
def create_alert(
    payload: AlertCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a price alert for a tracked product."""
    # Verify user tracks this product
    tracker = db.query(models.UserTrackedProduct).filter(
        models.UserTrackedProduct.user_id == current_user.id,
        models.UserTrackedProduct.product_id == payload.product_id,
    ).first()
    if not tracker:
        raise HTTPException(status_code=404, detail="Product not in your tracking list. Add it first.")

    product = db.query(models.Product).filter(models.Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    alert = models.PriceAlert(
        user_id=current_user.id,
        product_id=payload.product_id,
        alert_type=payload.alert_type,
        target_price=payload.target_price,
        minimum_price=payload.minimum_price,
        maximum_price=payload.maximum_price,
        percentage_drop=payload.percentage_drop,
        base_price=product.current_price,  # Snapshot price when alert is set
        alert_status=models.AlertStatusEnum.active,
        notify_email=payload.notify_email,
        notify_push=payload.notify_push,
        notify_sms=payload.notify_sms,
        notify_in_app=payload.notify_in_app,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("", response_model=List[AlertOut])
def list_alerts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    status_filter: Optional[str] = None,
):
    query = db.query(models.PriceAlert).filter(
        models.PriceAlert.user_id == current_user.id
    )
    if status_filter:
        query = query.filter(models.PriceAlert.alert_status == status_filter)
    return query.order_by(models.PriceAlert.created_at.desc()).all()


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    alert = db.query(models.PriceAlert).filter(
        models.PriceAlert.id == alert_id,
        models.PriceAlert.user_id == current_user.id,
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.put("/{alert_id}", response_model=AlertOut)
def update_alert(
    alert_id: int,
    payload: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    alert = db.query(models.PriceAlert).filter(
        models.PriceAlert.id == alert_id,
        models.PriceAlert.user_id == current_user.id,
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(alert, field, value)
    alert.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    alert = db.query(models.PriceAlert).filter(
        models.PriceAlert.id == alert_id,
        models.PriceAlert.user_id == current_user.id,
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
