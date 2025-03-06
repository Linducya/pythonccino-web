from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import bcrypt
import secrets  # Import the secrets module

# Load environment variables from .env file
load_dotenv()

# Secret key to encode and decode JWT tokens
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory store for MFA codes (for demonstration purposes)
mfa_codes = {}

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

def generate_mfa_code(username: str):
    code = secrets.token_hex(3)  # Generate a 6-character hex code
    mfa_codes[username] = code
    # Send the code to the user (e.g., via email or SMS)
    print(f"MFA code for {username}: {code}")

def verify_mfa_code(username: str, code: str):
    return mfa_codes.get(username) == code

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as e:
        print(f"JWTError: {e}")
        raise credentials_exception
    return {"username": username}