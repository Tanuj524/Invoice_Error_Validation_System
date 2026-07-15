# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..mailer import send_password_reset_email



from datetime import datetime, timedelta, timezone
from ..models import PasswordResetToken
from ..config import settings
from ..db import get_db
from ..models import User, UserRole
from ..Oauth import generate_reset_token, hash_reset_token, hash_password, verify_password_or_dummy, create_access_token, get_current_user, RESET_TOKEN_EXPIRE_MINUTES
from .. import schemas

router = APIRouter(prefix="/auth", tags=["auth"])

limiter = Limiter(key_func=get_remote_address)






@router.post("/register", response_model=schemas.UserOut, status_code=201)
@limiter.limit("5/minute")
def register(request: Request, payload: schemas.UserIn, db: Session = Depends(get_db)):
    existing = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(409, "Email already registered")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.USER, 
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login")
@limiter.limit("10/minute")
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.execute(
        select(User).where(User.email == form_data.username)
    ).scalar_one_or_none()

    
    password_ok = verify_password_or_dummy(
        form_data.password, user.hashed_password if user else None
    )
    if not user or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

  
    token = create_access_token(data={"user_id": user.id})
    response.set_cookie(
        key="jwt",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=86400,
        secure=True if settings.ENVIRONMENT == "production" else False,
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/forgot-password")
@limiter.limit("3/minute")
def forgot_password(request: Request, payload: schemas.ForgotPasswordIn, db: Session = Depends(get_db)):
    user = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()

   
    generic_response = {"message": "If that email is registered, a reset link has been sent."}

    if not user or not user.is_active:
        return generic_response

   
    db.execute(
        select(PasswordResetToken)
        .where(PasswordResetToken.user_id == user.id, PasswordResetToken.used_at.is_(None))
    )
    old_tokens = db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
    ).scalars().all()
    for t in old_tokens:
        db.delete(t)

    raw_token, token_hash = generate_reset_token()
    reset_entry = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
    )
    db.add(reset_entry)
    db.commit()

    
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
    
    send_password_reset_email(user.email, reset_link)
    return generic_response


@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(request: Request, payload: schemas.ResetPasswordIn, db: Session = Depends(get_db)):
    token_hash = hash_reset_token(payload.token)

    entry = db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    ).scalar_one_or_none()

    invalid_exc = HTTPException(400, "Invalid or expired reset token")

    if not entry:
        raise invalid_exc
    if entry.used_at is not None:
        raise invalid_exc
    if entry.expires_at < datetime.now(timezone.utc):
        raise invalid_exc

    user = db.get(User, entry.user_id)
    if not user or not user.is_active:
        raise invalid_exc

    user.hashed_password = hash_password(payload.new_password)
    entry.used_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Password has been reset successfully. Please log in."}



@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("jwt")
    return {"message": "Logged out successfully"}