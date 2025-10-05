from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd.verify(plain, hashed)


def hash_password(plain: str) -> str:
    hashed = pwd.hash(plain)
    return hashed


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
