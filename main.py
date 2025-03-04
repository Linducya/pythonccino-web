from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_404_NOT_FOUND
from app.utils import load_data, save_data
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if (exc.status_code == HTTP_404_NOT_FOUND):
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

@app.get("/order_food", response_class=HTMLResponse)
async def get_order_food(request: Request):
    food_menu, book_menu = load_data()
    return templates.TemplateResponse("order_food.html", {"request": request, "food_menu": food_menu})

@app.post("/order_food", response_class=HTMLResponse)
async def post_order_food(request: Request, name: str = Form(...), email: str = Form(None), food_item: str = Form(...), quantity: int = Form(...), email_confirmation: bool = Form(False)):
    # Load the food menu to get the description
    food_menu, _ = load_data()
    food_description = next((item["description"] for item in food_menu if item["name"] == food_item), "No description available")

    order_details = {
        "food_item": food_item,
        "description": food_description,
        "quantity": quantity
    }
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
        # Append the new order to the existing customer's orders
        customer_order["orders"].append(order_details)
    else:
        # Create a new customer order
        new_customer_order = {
            "name": name,
            "orders": [order_details]
        }
        orders.append(new_customer_order)

    # Write updated orders back to the file
    with open(orders_file_path, "w") as f:
        json.dump(orders, f, indent=4)

    # Send email confirmation if requested
    if email_confirmation and email:
        send_email_confirmation(name, email, order_details)

    return templates.TemplateResponse("order_confirmation.html", {"request": request, "order_details": order_details, "order_type": "food"})

# Function to send email confirmation. Use an app-specific password with 2FA enabled.
def send_email_confirmation(name, email, order_details):
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    receiver_email = email

    # Create the email content
    message = MIMEMultipart("alternative")
    message["Subject"] = "Order Confirmation"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"Dear {name},\n\nThank you for your order!\n\nOrder Details:\nFood Item: {order_details['food_item']}\nDescription: {order_details['description']}\nQuantity: {order_details['quantity']}\n\nBest regards,\nYour Restaurant"
    html = f"""\
    <html>
    <body>
        <p>Dear {name},<br><br>
           Thank you for your order!<br><br>
           <b>Order Details:</b><br>
           Food Item: {order_details['food_item']}<br>
           Description: {order_details['description']}<br>
           Quantity: {order_details['quantity']}<br><br>
           Best regards,<br>
           The Pythonccino Food & Book Cafe
        </p>
    </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    # Send the email. Use Gmail's SMTP server using SSL
    # Change the port and smtp_server if you're using a different email provider
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

@app.get("/order_book", response_class=HTMLResponse)
async def get_order_book(request: Request):
    food_menu, book_menu = load_data()
    return templates.TemplateResponse("order_book.html", {"request": request, "book_menu": book_menu})  

@app.post("/order_book", response_class=HTMLResponse)
async def post_order_book(request: Request, name: str = Form(...), book_title: str = Form(...), quantity: int = Form(...)):
    order_details = {
        "name": name,
        "book_title": book_title,
        "quantity": quantity
    }
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
        # Append the new order to the existing customer's orders
        customer_order["orders"].append(order_details)
    else:
        # Create a new customer order
        new_customer_order = {
            "name": name,
            "orders": [order_details]
        }
        orders.append(new_customer_order)

    # Write updated orders back to the file
    with open(orders_file_path, "w") as f:
        json.dump(orders, f, indent=4)

    return templates.TemplateResponse("order_confirmation.html", {"request": request, "order_details": order_details, "order_type": "book"})