from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from typing import Optional
from auth import get_password_hash, verify_password, create_access_token, authenticate_user
from models import User, UserCreate, UserRead
from database import get_session
from datetime import timedelta
from pydantic import BaseModel, EmailStr

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

@router.post("/register", response_model=UserRead)
def register(register_request: RegisterRequest, session: Session = Depends(get_session)):
    """Register a new user"""
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == register_request.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Validate name length
    if not register_request.name or len(register_request.name.strip()) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name is required"
        )

    if len(register_request.name.strip()) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name must be less than 100 characters"
        )

    # Validate email format (handled by EmailStr but we can add additional checks)
    email = register_request.email.lower().strip()
    if len(email) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email must be less than 255 characters"
        )

    # Validate password length
    if len(register_request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    if len(register_request.password.encode('utf-8')) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password exceeds 72 bytes, please use a shorter password"
        )

    # Hash the password
    hashed_password = get_password_hash(register_request.password)

    # Create new user
    user = User(
        id=register_request.email,  # Using email as ID for simplicity
        email=register_request.email,
        name=register_request.name.strip(),
        password_hash=hashed_password
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Return user object without password_hash
    return UserRead(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.post("/login")
def login(login_request: LoginRequest, session: Session = Depends(get_session)):
    """Login and return JWT token"""
    email = login_request.email.lower().strip()
    password = login_request.password

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )

    # Additional validation
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    user = authenticate_user(session, email, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
    access_token_expires = timedelta(minutes=10080)  # 7 days
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }