from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.services.security import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60

# =========================
# JWT SCHEME
# =========================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# =========================
# REGISTER
# =========================
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):

    username = (user.username or "").strip()
    email = (user.email or "").strip().lower()
    password = user.password

    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="All fields are required")

    try:
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        new_user = User(
            username=username,
            email=email,
            password=hash_password(password),
            role="user"
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User registered successfully",
            "user_id": new_user.id
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        print("REGISTER ERROR:", repr(e))
        raise HTTPException(status_code=500, detail="Registration failed")


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    username = (user.username or "").strip()
    password = user.password

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")

    try:
        db_user = db.query(User).filter(User.username == username).first()

        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        try:
            valid = verify_password(password, db_user.password)
        except Exception as e:
            print("VERIFY ERROR:", repr(e))
            raise HTTPException(status_code=500, detail="Authentication system error")

        if not valid:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token(
            data={
                "sub": db_user.username,
                "role": db_user.role,
                "user_id": db_user.id
            },
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email,
                "role": db_user.role
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        print("LOGIN ERROR:", repr(e))
        raise HTTPException(status_code=500, detail="Login failed")


# ======================================================
# 🔐 NEW: GET CURRENT USER (PROTECTED ROUTE BASE)
# ======================================================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ======================================================
# 🔐 NEW: ROLE CHECK (ADMIN ONLY)
# ======================================================
def admin_required(current_user: User = Depends(get_current_user)):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user