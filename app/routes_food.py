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

ORDERS_FILE_PATH = os.environ.get("ORDERS_FOOD_FILE", "data/orders_food.json")


@router.get(
    "/add_food",
    response_class=HTMLResponse,
    dependencies=[Depends(get_current_user)]
)
async def get_add_food(request: Request):
    return templates.TemplateResponse("add_food.html", {"request": request})


@router.post(
    "/add_food",
    response_class=HTMLResponse,
    dependencies=[Depends(get_current_user)]
)
async def post_add_food(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...)
):
    food_menu, book_menu = load_data()
    new_food = {
        "name": name,
        "description": description,
        "price": price
    }
    food_menu.append(new_food)
    save_data(food_menu, book_menu)
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "food_menu": food_menu, "book_menu": book_menu}
    )


@router.get("/order_food", response_class=HTMLResponse)
async def get_order_food(request: Request):
    food_menu, _ = load_data()
    return templates.TemplateResponse(
        "order_food.html", {"request": request, "food_menu": food_menu}
    )


@router.post("/order_food", response_class=HTMLResponse)
async def post_order_food(
    request: Request,
    name: str = Form(...),
    email: str = Form(None),
    email_confirmation: bool = Form(False),
    food_item: list = Form(...),
    quantity: list = Form(...)
):
    # Load the food menu to get the descriptions
    food_menu, _ = load_data()
    order_details = []
    order_number = str(uuid.uuid4())  # Generate a unique order number
    total_amount = 0
    for item, qty in zip(food_item, quantity):
        qty = int(qty)  # Convert quantity to integer
        food_description = next(
            (i["description"] for i in food_menu if i["name"] == item), "No desc"
        )
        price = next((i["price"] for i in food_menu if i["name"] == item), 0)
        total_amount += price * qty
        order_details.append({
            "order_number": order_number,
            "name": name,
            "food_item": item,
            "description": food_description,
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
        send_email_confirmation(name, email, order_details)
    return templates.TemplateResponse(
        "order_confirmation.html",
        {
            "request": request,
            "order_details": order_details,
            "order_type": "food",
            "total_amount": total_amount
        }
    )
