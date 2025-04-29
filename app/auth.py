# Description auth.py: This file contains the authentication logic for the FastAPI application.
# It includes functions to hash and verify passwords, authenticate users, create access tokens,
# and get the current user from a JWT token. It also includes functions to generate and verify
# TOTP codes for two-factor authentication. 
from app.db import store_totp_secret, get_totp_secret
from app.exceptions import credentials_exception
from fastapi import HTTPException, status, Depends, Request
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import bcrypt
import pyotp  # Import the pyotp module
import logging

# Load environment variables from .env file
load_dotenv()

# Create a logger
logger = logging.getLogger(__name__)

# Secret key to encode and decode JWT tokens
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("SECRET_KEY is missing from environment variables")

PEPPER_SECRET = os.getenv("PEPPER_SECRET")
if not PEPPER_SECRET:
    raise ValueError("PEPPER_SECRET is missing from environment variables")

# Algorithm to encode and decode JWT tokens
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory store for TOTP secrets (for demonstration purposes)
totp_secrets = {}

def hash_password(password: str) -> str:
    """Hashes the password with a peppered value and bcrypt."""
    peppered_password = password + PEPPER_SECRET
    return bcrypt.hashpw(peppered_password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
    # return bcrypt.hashpw(peppered_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    peppered_password = plain_password + PEPPER_SECRET
    return bcrypt.checkpw(peppered_password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(username: str, password: str):
    correct_username = os.getenv("STAFF_USERNAME")
    correct_password_hash = os.getenv("STAFF_PASSWORD")
    if username == correct_username and verify_password(password, correct_password_hash):
        return {"username": username}
    return None

def create_access_token(data: dict):
    # expire = datetime.utcnow() + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    to_encode = data.copy()
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "scope": "access"})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

async def generate_totp_secret(username: str):
    """Generate a TOTP secret, store it, and return a provisioning URI."""
    secret = pyotp.random_base32()
    await store_totp_secret(username, secret)  # Store in database
    
    # Generate a TOTP URI following the correct format
    totp = pyotp.TOTP(secret)
    totp_uri = totp.provisioning_uri(name=username, issuer_name="Pythonccino")
    # print(f"Generated TOTP URI for {username}: {totp_uri}")
    return {"totp_uri": totp_uri}
    
    # Display the TOTP URI as a QR code or link for the user to scan with their authenticator app
    # totp_uri = pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name="Pythonccino")
    # print(f"TOTP URI for {username}: {totp_uri}")
    # return {"totp_uri": totp_uri}

async def verify_totp_code(username: str, code: str) -> bool:
    """Verify the provided TOTP code against the stored secret."""
    logger.info("verify_totp_code function has been called.")
    secret = await get_totp_secret(username)
    if not secret:
        raise HTTPException(status_code=400, detail="TOTP secret not found for this user")
    
    logger.info(f"Verifying TOTP code for username: {username}")
    logger.info(f"Stored secret: {secret}")
    logger.info(f"Provided code: {code}")
    
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)  # Allow slight clock drift

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    """Extracts the current user from the token, checking both headers and query parameters."""
    if not token:
        token = request.query_params.get("token")  # Fallback to URL token
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        user = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])  # Token verification logic
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return user

# def get_current_user(token: str = Depends(oauth2_scheme)):
    # """Extracts and verifies the current user from the JWT token."""
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Could not validate credentials",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    # try:
    #     payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    #     username: str = payload.get("sub")
    #     if not username:
    #         raise credentials_exception
    #     return {"username": username}
    # except JWTError as e:
    #     logger.warning(f"JWT decoding failed: {e}")  # Log the error
    #     raise credentials_exception
    
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid token",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         return {"username": username}
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )