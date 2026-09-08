from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core.security import decode_token
from db.database import get_db
from db import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    sub_val = payload.get("sub")
    if sub_val is None:
        raise credentials_exception
    user = None
    if str(sub_val).isdigit():
        user = db.query(models.User).filter(models.User.id == int(sub_val)).first()
    else:
        user = db.query(models.User).filter(models.User.email == str(sub_val)).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def get_current_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


oauth2_optional_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user_optional(
    token: str = Depends(oauth2_optional_scheme), db: Session = Depends(get_db)
) -> models.User:
    if not token:
        return None
    try:
        payload = decode_token(token)
        if not payload:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None
