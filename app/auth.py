from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import bcrypt
import pyotp  # Import the pyotp module

# Load environment variables from .env file
load_dotenv()

# Secret key to encode and decode JWT tokens
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory store for TOTP secrets (for demonstration purposes)
totp_secrets = {}

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(username: str, password: str):
    correct_username = os.getenv("STAFF_USERNAME")
    correct_password_hash = os.getenv("STAFF_PASSWORD")
    if username == correct_username and verify_password(password, correct_password_hash):
        return {"username": username}
    return None

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_totp_secret(username: str):
    secret = pyotp.random_base32()
    totp_secrets[username] = secret
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name="Pythonccino")
    # Display the TOTP URI as a QR code or link for the user to scan with their authenticator app
    print(f"TOTP URI for {username}: {totp_uri}")
    return totp_uri

def verify_totp_code(username: str, code: str):
    secret = totp_secrets.get(username)
    if not secret:
        return False
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

# def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#     except JWTError as e:
#         print(f"JWTError: {e}")
#         raise credentials_exception
#     return {"username": username}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"username": username}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )