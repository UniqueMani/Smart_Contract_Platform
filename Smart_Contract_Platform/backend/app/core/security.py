from datetime import datetime, timedelta
from typing import Any, Optional
from jose import jwt
from passlib.context import CryptContext

from .config import settings

"""Password hashing.

We intentionally use PBKDF2 here instead of bcrypt.

Reason: `passlib[bcrypt]` can be incompatible with `bcrypt>=4` in some Windows
environments (it may error during backend detection and password hashing).
PBKDF2 is built into passlib and works reliably across platforms.
"""

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str, role: str, company: Optional[str] = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_exp_minutes)
    to_encode: dict[str, Any] = {"exp": expire, "sub": subject, "role": role}
    if company:
        to_encode["company"] = company
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)

def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
