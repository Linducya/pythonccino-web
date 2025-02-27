# Helper function (Handles JSON Read/Write)
import json
import os

# Define base directory where JSON files are stored
# BASE_DIR gets the absolute directory path of the current script (run.py)
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Moves up one level to the parent directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(BASE_DIR)

# DATA_DIR is the relative path to the data/ folder
DATA_DIR = os.path.join(BASE_DIR, 'data')
# print(DATA_DIR)

# Construct the full path to the JSON files
food_menu_path = os.path.join(DATA_DIR, 'food_menu.json')
book_menu_path = os.path.join(DATA_DIR, 'book_menu.json')

# Function loads food and book menus from JSON files - json.load(file) method
def load_data():
    try:
        with open(food_menu_path, 'r') as file:
            food_menu = json.load(file)
        with open(book_menu_path, 'r') as file:
            book_menu = json.load(file)
    except FileNotFoundError as e:
        print(f"Error: {e}. Ensure the JSON files are in the correct directory.")
        food_menu = []
        book_menu = []
    return food_menu, book_menu

# Function writes contents of food_menu & book_menu variables to JSON files:
def save_data(food_menu, book_menu):
    with open(food_menu_path, 'w') as file:
        json.dump(food_menu, file, indent=4)
    with open(book_menu_path, 'w') as file:
        json.dump(book_menu, file, indent=4)
