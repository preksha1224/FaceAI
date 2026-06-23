from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

load_dotenv()

# 🔐 Safe environment fallback (prevents crash)
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# 🔐 Switch to argon2 (recommended, avoids bcrypt issues)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# =========================
# PASSWORD HASHING
# =========================
def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print("VERIFY ERROR:", repr(e))
        return False


# =========================
# JWT TOKEN CREATION (FIXED)
# =========================
def create_access_token(data: dict, expires_delta: timedelta | None = None):

    to_encode = data.copy()

    # ⏱ Safe expiry handling
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(hours=2)
    )

    to_encode.update({"exp": expire})

    try:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        print("JWT ERROR:", repr(e))
        raise