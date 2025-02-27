from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_404_NOT_FOUND
from app.utils import load_data, save_data

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == HTTP_404_NOT_FOUND:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse("error.html", {"request": request, "detail": exc.detail}, status_code=exc.status_code)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def read_home(request: Request):
    try:
        food_menu, book_menu = load_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        food_menu, book_menu = [], []
    return templates.TemplateResponse("home.html", {"request": request, "food_menu": food_menu, "book_menu": book_menu})

@app.get("/add_food", response_class=HTMLResponse)
async def get_add_food(request: Request):
    return templates.TemplateResponse("add_food.html", {"request": request})

@app.post("/add_food", response_class=HTMLResponse)
async def post_add_food(request: Request, name: str = Form(...), description: str = Form(...), price: float = Form(...)):
    food_menu, book_menu = load_data()
    new_food = {"name": name, "description": description, "price": price}
    food_menu.append(new_food)
    save_data(food_menu, book_menu)
    return templates.TemplateResponse("home.html", {"request": request, "food_menu": food_menu, "book_menu": book_menu})

@app.get("/add_book", response_class=HTMLResponse)
async def get_add_book(request: Request):
    return templates.TemplateResponse("add_book.html", {"request": request})

@app.post("/add_book", response_class=HTMLResponse)
async def post_add_book(request: Request, title: str = Form(...), year_published: str = Form(...), price: float = Form(...)):
    food_menu, book_menu = load_data()
    new_book = {"title": title, "year_published": year_published, "price": price}
    book_menu.append(new_book)
    save_data(food_menu, book_menu)
    return templates.TemplateResponse("home.html", {"request": request, "food_menu": food_menu, "book_menu": book_menu})