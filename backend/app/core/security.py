import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

APP_ENV = os.getenv("APP_ENV", "development").lower()
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-change-this-secret")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET", "dev-only-change-this-refresh-secret")
if APP_ENV == "production" and (
    not JWT_SECRET or JWT_SECRET in {"dev-only-change-this-secret", "change-me-in-production", "replace-with-a-long-random-secret"}
):
    raise RuntimeError("JWT_SECRET must be configured with a strong value in production.")
if APP_ENV == "production" and (
    not JWT_REFRESH_SECRET or JWT_REFRESH_SECRET in {"dev-only-change-this-refresh-secret", "change-me-in-production"}
):
    raise RuntimeError("JWT_REFRESH_SECRET must be configured with a strong value in production.")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "60"))
JWT_REFRESH_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))


def get_allowed_origins(raw_origins: str | None = None) -> list[str]:
    csv_value = raw_origins or os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in csv_value.split(",") if origin.strip()]


def build_security_headers() -> dict[str, str]:
    headers: dict[str, str] = {
        "x-content-type-options": "nosniff",
        "x-frame-options": "DENY",
        "x-xss-protection": "1; mode=block",
        "referrer-policy": "strict-origin-when-cross-origin",
        "content-security-policy": "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none';",
    }

    if APP_ENV == "production":
        headers["strict-transport-security"] = "max-age=31536000; includeSubDomains"
    else:
        headers["strict-transport-security"] = "max-age=300; includeSubDomains"

    return headers


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, digest_hex = stored_hash.split("$", 1)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 120_000)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int, expires_minutes: int | None = None) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes or JWT_ACCESS_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "type": "access", "exp": expires_at}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: int, expires_days: int | None = None) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days or JWT_REFRESH_EXPIRE_DAYS)
    return jwt.encode({"sub": str(user_id), "type": "refresh", "exp": expires_at}, JWT_REFRESH_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    if payload.get("type") not in {None, "access"}:
        raise jwt.InvalidTokenError("Token inválido para acceso")
    subject = payload.get("sub")
    if subject is None:
        raise jwt.InvalidTokenError("Token sin usuario")
    return int(subject)


def decode_refresh_token(token: str) -> int:
    payload = jwt.decode(token, JWT_REFRESH_SECRET, algorithms=[JWT_ALGORITHM])
    if payload.get("type") != "refresh":
        raise jwt.InvalidTokenError("Token inválido para refresh")
    subject = payload.get("sub")
    if subject is None:
        raise jwt.InvalidTokenError("Token sin usuario")
    return int(subject)