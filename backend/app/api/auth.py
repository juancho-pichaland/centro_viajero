import os

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.security import create_access_token, create_refresh_token, decode_refresh_token, hash_password, verify_password
from ..db.dependencies import get_db
from ..models import Usuario
from ..schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
COOKIE_SECURE = os.getenv("APP_ENV", "development").lower() == "production"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=60 * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )


@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.scalar(select(Usuario).where(Usuario.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="El correo ya está registrado")
    user = Usuario(nombre=payload.nombre, email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post('/login', response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(Usuario).where(Usuario.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    _set_auth_cookies(response, access_token, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "user": user}


@router.post('/refresh', response_model=AuthResponse)
def refresh_token(payload: RefreshTokenRequest, response: Response, db: Session = Depends(get_db)):
    try:
        user_id = decode_refresh_token(payload.refresh_token)
    except Exception as exc:  # pragma: no cover - validation path
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado") from exc

    user = db.scalar(select(Usuario).where(Usuario.id == user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    _set_auth_cookies(response, access_token, refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }
