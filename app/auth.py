# This file contains the authentication logic for the FastAPI application.
# Includes functions to hash & verify passwords, authenticate users,
# create access tokens, and get current user from a JWT token.  Includes
# functions to generate and verify TOTP codes for two-factor authentication.
from app.db import store_totp_secret, get_totp_secret
from fastapi import HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import bcrypt
import pyotp
import logging
from jose import JWTError, jwt

# Load environment variables from .env file
load_dotenv()

# Create a logger
logger = logging.getLogger(__name__)

# Secret key to encode and decode JWT tokens
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY is missing from environment variables")

PEPPER_SECRET = os.getenv("PEPPER_SECRET")
if not PEPPER_SECRET:
    raise ValueError("PEPPER_SECRET is missing from environment variables")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password: str) -> str:
    """Hashes the password with a peppered value and bcrypt."""
    peppered_password = password + PEPPER_SECRET
    return bcrypt.hashpw(
        peppered_password.encode("utf-8"),
        bcrypt.gensalt(rounds=12)
    ).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    peppered_password = plain_password + PEPPER_SECRET
    return bcrypt.checkpw(
        peppered_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def authenticate_user(username: str, password: str):
    correct_username = os.getenv("STAFF_USERNAME")
    correct_password_hash = os.getenv("STAFF_PASSWORD")
    if (
        username == correct_username
        and verify_password(password, correct_password_hash)
    ):
        return {"username": username}
    return None


def create_access_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = data.copy()
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "scope": "access"
    })
    return jwt.encode(
        to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM
    )


async def generate_totp_secret(username: str):
    """Generate a TOTP secret, store it, and return a provisioning URI."""
    secret = pyotp.random_base32()
    await store_totp_secret(username, secret)
    totp = pyotp.TOTP(secret)
    totp_uri = totp.provisioning_uri(
        name=username, issuer_name="Pythonccino"
    )
    return {"totp_uri": totp_uri}


async def verify_totp_code(username: str, code: str) -> bool:
    """Verify the provided TOTP code against the stored secret."""
    secret = await get_totp_secret(username)
    if not secret:
        raise HTTPException(
            status_code=400, detail="TOTP secret not found for this user"
        )
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


async def get_current_user(
    request: Request, token: str = Depends(oauth2_scheme)
):
    # Extracts current user from the token, checking both headers & query parameters.
    if not token:
        token = request.query_params.get("token")
    if not token:
        raise HTTPException(
            status_code=401, detail="Not authenticated"
        )
    try:
        user = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid token"
        )
    return user
