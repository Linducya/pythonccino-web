"""
utils_data.py
Helper functions for reading and writing food and book menu data to JSON files.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
food_menu_path = os.environ.get('FOOD_MENU_PATH', os.path.join(DATA_DIR, 'food_menu.json'))
book_menu_path = os.environ.get('BOOK_MENU_PATH', os.path.join(DATA_DIR, 'book_menu.json'))

def load_data():
    try:
        with open(food_menu_path, 'r') as file:
            food_menu = json.load(file)
        with open(book_menu_path, 'r') as file:
            book_menu = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        food_menu = []
        book_menu = []
    return food_menu, book_menu

def save_data(food_menu, book_menu):
    try:
        with open(food_menu_path, 'w') as file:
            json.dump(food_menu, file, indent=4)
        with open(book_menu_path, 'w') as file:
            json.dump(book_menu, file, indent=4)
        return True
    except Exception:
        return False
