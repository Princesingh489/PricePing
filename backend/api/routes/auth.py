import secrets
import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from db.database import get_db
from db import models
from core.config import settings
from core.security import verify_password, get_password_hash, create_access_token
from core.deps import get_current_user
from schemas.schemas import (
    UserRegister, UserLogin, Token, UserOut, UserUpdate, ForgotPassword, GoogleAuthRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    clean_email = payload.email.lower().strip()
    existing = db.query(models.User).filter(models.User.email == clean_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        name=payload.name.strip(),
        email=clean_email,
        password_hash=get_password_hash(payload.password),
        phone_number=payload.phone_number,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    clean_email = form_data.username.lower().strip()
    user = db.query(models.User).filter(models.User.email == clean_email).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.post("/login/json", response_model=Token)
def login_json(payload: UserLogin, db: Session = Depends(get_db)):
    """JSON login endpoint (alternative to OAuth2 form)."""
    clean_email = payload.email.lower().strip()
    user = db.query(models.User).filter(models.User.email == clean_email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.post("/google", response_model=Token)
async def google_auth(payload: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Authenticate via Google OAuth 2.0.
    Accepts:
    - `code`: Authorization code to exchange with Google using client credentials.
    - `credential`: Google ID token to verify via Google's tokeninfo service.
    """
    email = None
    name = None

    if payload.code:
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            logger.error("Google OAuth client credentials not configured on backend.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth is not configured on the server. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
            )

        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": payload.code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": payload.redirect_uri or "http://localhost:5173/auth/google/callback",
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                token_resp = await client.post(token_url, data=token_data)
            except Exception as exc:
                logger.error(f"Error connecting to Google OAuth token endpoint: {exc}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to connect to Google OAuth service."
                )

            if token_resp.status_code != 200:
                logger.warning(f"Google token exchange failed: {token_resp.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to authenticate with Google. The authorization code may be invalid or expired."
                )

            tokens = token_resp.json()
            access_token = tokens.get("access_token")

            try:
                userinfo_resp = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
            except Exception as exc:
                logger.error(f"Error connecting to Google userinfo endpoint: {exc}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to retrieve Google user profile."
                )

            if userinfo_resp.status_code != 200:
                logger.warning(f"Google userinfo failed: {userinfo_resp.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not retrieve account details from Google."
                )

            user_info = userinfo_resp.json()
            email = user_info.get("email")
            name = user_info.get("name") or user_info.get("given_name") or (email.split("@")[0] if email else "User")

    elif payload.credential:
        tokeninfo_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={payload.credential}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(tokeninfo_url)
            except Exception as exc:
                logger.error(f"Error connecting to Google tokeninfo: {exc}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to connect to Google verification service."
                )

            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired Google credential."
                )

            info = resp.json()
            if settings.GOOGLE_CLIENT_ID and info.get("aud") != settings.GOOGLE_CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google credential audience mismatch."
                )

            email = info.get("email")
            name = info.get("name") or (email.split("@")[0] if email else "User")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either authorization 'code' or 'credential' must be provided."
        )

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account did not provide an email address."
        )

    clean_email = email.lower().strip()
    user = db.query(models.User).filter(models.User.email == clean_email).first()

    if not user:
        # Create a new user account with a secure randomized password
        random_password = secrets.token_urlsafe(32)
        user = models.User(
            name=name.strip() if name else clean_email.split("@")[0],
            email=clean_email,
            password_hash=get_password_hash(random_password),
            is_active=True,
            is_admin=False,
            email_notifications=True,
            push_notifications=True,
            sms_notifications=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is inactive")

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(payload: UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/forgot-password")
def forgot_password(payload: ForgotPassword, db: Session = Depends(get_db)):
    """Placeholder for password reset flow (email token sending)."""
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    # Always return success to prevent email enumeration
    return {"message": "If this email exists, a password reset link has been sent."}


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # BUG-001 FIX: Passwords now received in request body (not URL query params).
    # Query params are logged by web servers, proxies, and load balancers.
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    if len(payload.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    current_user.password_hash = get_password_hash(payload.new_password)
    db.commit()
    return {"message": "Password updated successfully"}
