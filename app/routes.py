# Create Web Routes: Define routes in Flask that correspond to the operations your app performs, like displaying menus, adding food items, etc. 
# These routes replace the functionality of the command-line interface.
import os
from flask import Blueprint, render_template, request, redirect, url_for
from app.utils import load_data, save_data

main = Blueprint('main', __name__)

# Main entry point route
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/home')
def home():
    try:
        food_menu, book_menu = load_data()  # Load fresh data every time the home route is accessed
        print("\nWelcome to Pythonccino!\nRoutes are working!")
        print("Current working directory:", os.getcwd())
        print("Templates directory:", os.path.join(os.getcwd(), 'templates'))
        # print("Loaded Food Menu:", food_menu)
        # print("Loaded Book Menu:", book_menu)
    except Exception as e:
        print(f"Error loading data: {e}")
        food_menu, book_menu = [], []  # Default to empty lists if there's an error
    return render_template('home.html', food_menu=food_menu, book_menu=book_menu)

# Add other routes like adding food items, deleting items, etc.
# Add Food Item
@main.route('/add_food', methods=['GET', 'POST'])
def add_food():
    food_menu, book_menu = load_data()  # Load fresh data every time the add_food route is accessed
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        new_food = {"name": name, "description": description, "price": price}
        food_menu.append(new_food)
        save_data(food_menu, book_menu)
        return redirect(url_for('main.home'))
    return render_template('add_food.html')

# Add Book Item
@main.route('/add_book', methods=['GET', 'POST'])
def add_book():
    food_menu, book_menu = load_data()
    if request.method == 'POST':
        title = request.form['title']
        year_published = request.form['year_published']
        price = float(request.form['price'])
        new_book = {"title": title, "year_published": year_published, "price": price}
        book_menu.append(new_book)
        save_data(food_menu, book_menu)
        return redirect(url_for('main.home'))
    return render_template('add_book.html')
