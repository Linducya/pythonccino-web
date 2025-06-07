from fastapi import (
    APIRouter, Depends, Request, Form
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils_data import load_data, save_data
from app.utils_email import send_email_confirmation
from app.auth import get_current_user
import os
import uuid
import json

router = APIRouter()

# Define the templates object
TEMPLATES_DIR = os.environ.get("TEMPLATES_DIR", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

ORDERS_FILE_PATH = os.environ.get("ORDERS_BOOK_FILE", "data/orders_book.json")


@router.get(
    "/add_book",
    response_class=HTMLResponse,
    dependencies=[Depends(get_current_user)]
)
async def get_add_book(request: Request):
    return templates.TemplateResponse("add_book.html", {"request": request})


@router.post(
    "/add_book",
    response_class=HTMLResponse,
    dependencies=[Depends(get_current_user)]
)
async def post_add_book(
    request: Request,
    name: str = Form(...),
    author: str = Form(...),
    description: str = Form(...),
    price: float = Form(...)
):
    book_menu, food_menu = load_data()
    new_book = {
        "name": name,
        "author": author,
        "description": description,
        "price": price
    }
    book_menu.append(new_book)
    save_data(book_menu, food_menu)
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "book_menu": book_menu, "food_menu": food_menu}
    )


@router.get("/order_book", response_class=HTMLResponse)
async def get_order_book(request: Request):
    _, book_menu = load_data()
    return templates.TemplateResponse(
        "order_book.html", {"request": request, "book_menu": book_menu}
    )


@router.post("/order_book", response_class=HTMLResponse)
async def post_order_book(
    request: Request,
    name: str = Form(...),
    email: str = Form(None),
    email_confirmation: bool = Form(False),
    book_title: list = Form(...),
    quantity: list = Form(...)
):
    _, book_menu = load_data()  # Ensure book_menu is loaded
    order_details = []
    order_number = str(uuid.uuid4())  # Generate a unique order number
    total_amount = 0
    for title, qty in zip(book_title, quantity):
        qty = int(qty)
        price = next((i["price"] for i in book_menu if i["title"] == title), 0)
        total_amount += price * qty
        order_details.append({
            "order_number": order_number,
            "name": name,
            "book_title": title,
            "quantity": qty,
            "price": price
        })
    # Read existing orders
    try:
        if os.path.exists(ORDERS_FILE_PATH):
            with open(ORDERS_FILE_PATH, "r") as f:
                orders = json.load(f)
        else:
            orders = []
    except json.JSONDecodeError:
        orders = []
    customer_order = next((order for order in orders if order["name"] == name), None)
    if customer_order:
        if "orders" not in customer_order:
            customer_order["orders"] = []
        customer_order["orders"].extend(order_details)
    else:
        new_customer_order = {
            "name": name,
            "orders": order_details
        }
        orders.append(new_customer_order)
    with open(ORDERS_FILE_PATH, "w") as f:
        json.dump(orders, f, indent=4)
    if email_confirmation and email:
        send_email_confirmation(
            name,
            email,
            order_details,
            order_type="book"
        )
    return templates.TemplateResponse(
        "order_confirmation.html",
        {
            "request": request,
            "order_details": order_details,
            "order_type": "book",
            "total_amount": total_amount
        }
    )
