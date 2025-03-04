from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils_data import load_data, save_data
from app.utils_email import send_email_confirmation
import json
import os
import uuid

router = APIRouter()

# Define the templates object
templates = Jinja2Templates(directory="templates")

@router.get("/add_book", response_class=HTMLResponse)
async def get_add_book(request: Request):
    return templates.TemplateResponse("add_book.html", {"request": request})

@router.post("/add_book", response_class=HTMLResponse)
async def post_add_book(request: Request, title: str = Form(...), year_published: str = Form(...), price: float = Form(...)):
    food_menu, book_menu = load_data()
    new_book = {"title": title, "year_published": year_published, "price": price}
    book_menu.append(new_book)
    save_data(food_menu, book_menu)
    return templates.TemplateResponse("home.html", {"request": request, "food_menu": food_menu, "book_menu": book_menu})

@router.get("/order_book", response_class=HTMLResponse)
async def get_order_book(request: Request):
    food_menu, book_menu = load_data()
    return templates.TemplateResponse("order_book.html", {"request": request, "book_menu": book_menu})  

@router.post("/order_book", response_class=HTMLResponse)
async def post_order_book(request: Request, name: str = Form(...), email: str = Form(None), email_confirmation: bool = Form(False), book_title: list = Form(...), quantity: list = Form(...)):
    food_menu, book_menu = load_data()  # Ensure book_menu is loaded
    order_details = []
    order_number = str(uuid.uuid4())  # Generate a unique order number
    total_amount = 0
    for title, qty in zip(book_title, quantity):
        qty = int(qty)  # Convert quantity to integer
        price = next((i["price"] for i in book_menu if i["title"] == title), 0)
        total_amount += price * qty
        order_details.append({
            "order_number": order_number,
            "name": name,
            "book_title": title,
            "quantity": qty,
            "price": price
        })
    print(f"Order received: {order_details}")

    # Read existing orders
    orders_file_path = "data/orders_book.json"
    try:
        if os.path.exists(orders_file_path):
            with open(orders_file_path, "r") as f:
                orders = json.load(f)
        else:
            orders = []
    except json.JSONDecodeError as e:
        print(f"Error reading JSON file: {e}")
        orders = []

    # Find the customer in the existing orders
    customer_order = next((order for order in orders if order["name"] == name), None)
    if customer_order:
        # Ensure the 'orders' key exists
        if "orders" not in customer_order:
            customer_order["orders"] = []
        # Append the new orders to the existing customer's orders
        customer_order["orders"].extend(order_details)
    else:
        # Create a new customer order
        new_customer_order = {
            "name": name,
            "orders": order_details
        }
        orders.append(new_customer_order)

    # Write updated orders back to the file
    with open(orders_file_path, "w") as f:
        json.dump(orders, f, indent=4)

    # Send email confirmation if requested
    if email_confirmation and email:
        send_email_confirmation(name, email, order_details, order_type="book")

    return templates.TemplateResponse("order_confirmation.html", {"request": request, "order_details": order_details, "order_type": "book", "total_amount": total_amount})