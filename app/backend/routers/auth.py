# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..db import get_db
from ..models import User, UserRole
from ..Oauth import hash_password, verify_password_or_dummy, create_access_token, get_current_user
from .. import schemas

router = APIRouter(prefix="/auth", tags=["auth"])

# Shared limiter instance; registered on the app + exception handler in main.py
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=schemas.UserOut, status_code=201)
@limiter.limit("5/minute")
def register(request: Request, payload: schemas.UserIn, db: Session = Depends(get_db)):
    existing = db.execute(
        select(User).where(User.username == payload.username)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(409, "Username already taken")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.USER,  # new users are always USER by default
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

    # verify_password_or_dummy always performs a bcrypt comparison, even when
    # `user` is None, so this branch takes a similar amount of time whether
    # or not the email exists (mitigates user-enumeration via timing).
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

    # NOTE: role is intentionally NOT embedded in the token. Authorization
    # (require_admin / require_user) always re-checks the role from the
    # database on every request, so a stale/forged role claim can't grant
    # access. Keeping it out of the token avoids anyone assuming otherwise.
    token = create_access_token(data={"user_id": user.id})
    response.set_cookie(
        key="jwt",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=86400,
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("jwt")
    return {"message": "Logged out successfully"}