# main.py - Entry point for FastAPI application
from fastapi import (
    FastAPI, Request, Form, Depends, HTTPException
)
from fastapi.responses import (
    HTMLResponse, RedirectResponse, JSONResponse
)
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
import os
import logging
from dotenv import load_dotenv
from app.auth import (
    authenticate_user, create_access_token,
    generate_totp_secret, verify_totp_code
)
from app.utils_data import load_data
from app.routes_food import router as food_router
from app.routes_book import router as book_router

# Reconstruct Google OAuth credential files from environment variables (for Azure)
client_secret_json = os.getenv("GOOGLE_CLIENT_SECRET_JSON")
if client_secret_json:
    with open("client_secret.json", "w") as f:
        f.write(client_secret_json)

token_json = os.getenv("GOOGLE_TOKEN_JSON")
if token_json:
    with open("token.json", "w") as f:
        f.write(token_json)

# Load environment variables from .env file
load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"

# Ensure logging level is set to INFO
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Setup Jinja2 Templates
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


# 🟢 Route: Login Page (Frontend)
@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# 🟢 Route: Verify TOTP Page (Frontend)
@app.get("/verify_totp", response_class=HTMLResponse)
async def verify_totp_page(request: Request, username: str):
    return templates.TemplateResponse(
        "verify_totp.html", {"request": request, "username": username}
    )


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user, generate JWT access token, and return TOTP URI."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Generate TOTP Secret
    totp_data = await generate_totp_secret(user["username"])

    if not totp_data or "totp_uri" not in totp_data:
        raise HTTPException(
            status_code=500,
            detail="Error generating TOTP URI"
        )  # Ensure it never returns undefined

    totp_uri = totp_data["totp_uri"]  # Extract TOTP URI

    access_token = create_access_token(data={"sub": user["username"]})

    return JSONResponse(
        content={
            "access_token": access_token,
            "message": "TOTP URI generated",
            "totp_uri": totp_uri
        },
        status_code=200
    )


# 🟢 Route: Verify TOTP Code & Generate Access Token
@app.post("/verify_totp")
async def verify_totp(username: str = Form(...), code: str = Form(...)):
    """Verify user-provided TOTP code and return access token."""
    logger.info(
        f"/verify_totp route called with username: {username} and code: {code}"
    )

    if await verify_totp_code(username, code):
        access_token = create_access_token(data={"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(status_code=401, detail="Invalid TOTP code")


# 🟢 Route: Home Page (Frontend)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 🟢 Route: Load Home Page Data
@app.get("/home", response_class=HTMLResponse)
async def read_home(request: Request):
    try:
        food_menu, book_menu = load_data()
    except Exception:
        food_menu, book_menu = [], []
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "food_menu": food_menu,
            "book_menu": book_menu
        }
    )


@app.get("/staff", response_class=JSONResponse)
async def read_staff(request: Request):
    """Validate JWT token and return username."""
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is missing. Please include a valid token."
        )

    if not token.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header format is invalid. Expected 'Bearer <token>'."
        )

    logger.info(f"Authorization header received: {token}")

    token = token.split("Bearer ")[1]  # Extract actual token

    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=401,
                detail="Token payload missing 'sub' field."
            )
        return {"username": username}
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token validation error: {str(e)}"
        )


# 🟢 Route: Logout (Redirects to Login)
@app.get("/logout", response_class=RedirectResponse)
async def logout():
    """Clears token and redirects to login page."""
    response = RedirectResponse(url="/login")
    response.delete_cookie("token")  # Clears token if using cookies
    return response

# Include additional routers
app.include_router(food_router)
app.include_router(book_router)
