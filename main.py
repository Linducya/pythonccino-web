from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import authenticate_user, create_access_token, get_current_user, generate_totp_secret, verify_totp_code
from app.utils_data import load_data, save_data
from app.routes_food import router as food_router  # Import food_router
from app.routes_book import router as book_router  # Import book_router
from dotenv import load_dotenv
import os
import urllib.parse  # Import urllib.parse for URL encoding

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Setup Jinja2 Templates
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/verify_totp", response_class=HTMLResponse)
async def verify_totp(request: Request, username: str, totp_uri: str):
    return templates.TemplateResponse("verify_totp.html", {
        "request": request,
        "totp_uri": totp_uri,
        "username": username
    })

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    totp_uri = generate_totp_secret(user["username"])
    # encoded_totp_uri = urllib.parse.quote(totp_uri)  # URL-encode the TOTP URI
    access_token = create_access_token(data={"sub": user["username"]})

    return JSONResponse(
        content={
            "access_token": access_token,
            "message": "TOTP URI generated",
            "username": user["username"],
            "totp_uri": totp_uri  # Pass the raw TOTP URI here (not encoded, frontend will encode it)
        },
        status_code=200
    )

@app.post("/verify_totp")
async def verify_totp(username: str = Form(...), code: str = Form(...)):
    if verify_totp_code(username, code):
        access_token = create_access_token(data={"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def read_home(request: Request):
    try:
        food_menu, book_menu = load_data()
        print(f"Food Menu: {food_menu}")
        print(f"Book Menu: {book_menu}")
    except Exception as e:
        print(f"Error loading data: {e}")
        food_menu, book_menu = [], []
    return templates.TemplateResponse("home.html", {"request": request, "food_menu": food_menu, "book_menu": book_menu})

@app.get("/staff", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
async def read_staff(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("staff.html", {"request": request, "username": current_user["username"]})

app.include_router(food_router)
app.include_router(book_router)