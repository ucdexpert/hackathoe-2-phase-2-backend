from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from models import User
from database import get_session
from dotenv import load_dotenv
import os
import hashlib
import secrets

load_dotenv()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-at-least-32-characters-long")
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 7

# Security scheme for API docs
security_scheme = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-SHA256 with salt"""
    # Generate a random salt
    salt = secrets.token_hex(16)
    # Hash the password with the salt
    pwdhash = hashlib.pbkdf2_hmac('sha256',
                                  password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    # Encode as hex and store as "salt:hash"
    pwdhash = pwdhash.hex()
    return f"{salt}:{pwdhash}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    # Split the stored salt and hash
    salt, stored_hash = hashed_password.split(':')
    # Hash the provided password with the stored salt
    pwdhash = hashlib.pbkdf2_hmac('sha256',
                                  plain_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    # Compare the hashes
    return secrets.compare_digest(pwdhash.hex(), stored_hash)

def get_password_hash(password: str) -> str:
    """Alias for hash_password function"""
    return hash_password(password)

def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password"""
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> dict:
    """Verify JWT token and return payload"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception

def get_current_user_payload(token_data: dict = Depends(verify_token)) -> dict:
    """Get current user payload from token"""
    return token_data