from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils_data import load_data, save_data
from app.utils_email import send_email_confirmation
from app.auth import get_current_user
import json
import os
import uuid

router = APIRouter()

# Define the templates object
templates = Jinja2Templates(directory="templates")

@router.get("/add_food", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
async def get_add_food(request: Request):
    return templates.TemplateResponse("add_food.html", {"request": request})

@router.post("/add_food", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
async def post_add_food(request: Request, name: str = Form(...), description: str = Form(...), price: float = Form(...)):
    food_menu, book_menu = load_data()
    new_food = {"name": name, "description": description, "price": price}
    food_menu.append(new_food)
    save_data(food_menu, book_menu)
    return templates.TemplateResponse("home.html", {"request": request, "food_menu": food_menu, "book_menu": book_menu})

@router.get("/order_food", response_class=HTMLResponse)
async def get_order_food(request: Request):
    food_menu, book_menu = load_data()
    return templates.TemplateResponse("order_food.html", {"request": request, "food_menu": food_menu})

@router.post("/order_food", response_class=HTMLResponse)
async def post_order_food(request: Request, name: str = Form(...), email: str = Form(None), email_confirmation: bool = Form(False), food_item: list = Form(...), quantity: list = Form(...)):
    # Load the food menu to get the descriptions
    food_menu, _ = load_data()
    order_details = []
    order_number = str(uuid.uuid4())  # Generate a unique order number
    total_amount = 0
    for item, qty in zip(food_item, quantity):
        qty = int(qty)  # Convert quantity to integer
        food_description = next((i["description"] for i in food_menu if i["name"] == item), "No description available")
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
    print(f"Order received: {order_details}")

    # Read existing orders
    orders_file_path = "data/orders_food.json"
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
        send_email_confirmation(name, email, order_details)

    return templates.TemplateResponse("order_confirmation.html", {"request": request, "order_details": order_details, "order_type": "food", "total_amount": total_amount})