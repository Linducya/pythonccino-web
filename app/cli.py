# Description: Command Line Interface (CLI) for the Pythonccino Coffee & Book Cafe application
from app.utils import load_data, save_data

food_menu, book_menu = load_data()

# Function to display menus with numbered options
def display_menu_and_books():
    print("\nFood Menu:")
    for i, food in enumerate(food_menu, start=1):  # Number each menu item
        print(f"{i}. {food['name']} - {food['description']} (£{food['price']})")

    print("\nBook Menu:")
    for i, book in enumerate(book_menu, start=len(food_menu) + 1):  # Continue numbering after food menu
        print(f"{i}. {book['title']} ({book['year_published']}) - £{book['price']}")

# Function to calculate total basket value based on selected items
def calculate_total(basket):
    total_basket = sum([item['price'] for item in basket])
    print(f"Total basket value: £{total_basket:.2f}")
    return total_basket 

# Main function to run the application
def main():
    while True:  
        # Prompt the user to choose an option
        print("\nPlease choose an option:")
        print("1. Customer")
        print("2. Employee")
        print("3. Exit")
        option = input("Enter choice: ")

        if option == "1":
            # Customer flow
            print("\nWelcome, dear customer! Here's our menu:")
            display_menu_and_books()

            # Customer chooses items
            basket = []
            while True:
                choice = input("\nEnter the number of the item you want to add to your basket. To finish ordering enter 'done': ")
                if choice.lower() == 'done':
                    break
                
                # Validate input
                if choice.isdigit():
                    choice = int(choice)
                    # Check if the choice is valid for food
                    if 1 <= choice <= len(food_menu):
                        item = food_menu[choice - 1]
                        basket.append(item)
                        print(f"{item['name']} added to your basket!")
                    # Check if the choice is valid for books
                    elif len(food_menu) < choice <= len(food_menu) + len(book_menu):
                        item = book_menu[choice - len(food_menu) - 1]
                        basket.append(item)
                        print(f"{item['title']} added to your basket!")
                    else:
                        print("Invalid choice. Please enter a valid number.")
                else:
                    print("Invalid input. Please enter a number or enter 'done' to finish ordering.")

            # Display customer's order
            print("\nYour basket contains:")
            for item in basket:
                print(f"- {item['name'] if 'name' in item else item['title']} (£{item['price']})")

            # Calculate total basket value
            calculate_total(basket)

        elif option == "2":
            # Employee flow
            while True:
                print("\nEmployee Options:")
                print("1. View Menus")
                print("2. Add Food Item")
                print("3. Add Book Item")
                print("4. Delete Food Item")
                print("5. Delete Book Item")
                print("6. Exit to Main Menu")
                emp_option = input("Enter your choice: ")

                if emp_option == "1":
                    display_menu_and_books()

                elif emp_option == "2":
                    # Add a food item
                    name = input("Enter the name of the food item: ")
                    description = input("Enter the description: ")
                    price = float(input("Enter the price: "))
                    new_food = {"name": name, "description": description, "price": price}
                    food_menu.append(new_food)
                    save_data(food_menu, book_menu)
                    print(f"Food item '{name}' added successfully!")

                elif emp_option == "3":
                    # Add a book item
                    title = input("Enter the title of the book: ")
                    year_published = input("Enter the year published: ")
                    price = float(input("Enter the price: "))
                    new_book = {"title": title, "year_published": year_published, "price": price}
                    book_menu.append(new_book)
                    save_data(food_menu, book_menu)
                    print(f"Book '{title}' added successfully!")

                elif emp_option == "4":
                    # Delete a food item
                    display_menu_and_books()
                    food_choice = input("\nEnter the number of the food item to delete: ")
                    if food_choice.isdigit() and 1 <= int(food_choice) <= len(food_menu):
                        removed_food = food_menu.pop(int(food_choice) - 1)
                        save_data(food_menu, book_menu)
                        print(f"Food item '{removed_food['name']}' deleted successfully!")
                    else:
                        print("Invalid choice.")

                elif emp_option == "5":
                    # Delete a book item
                    display_menu_and_books()
                    book_choice = input("\nEnter the number of the book item to delete: ")
                    if book_choice.isdigit() and len(food_menu) < int(book_choice) <= len(food_menu) + len(book_menu):
                        removed_book = book_menu.pop(int(book_choice) - len(food_menu) - 1)
                        save_data(food_menu, book_menu)
                        print(f"Book '{removed_book['title']}' deleted successfully!")
                    else:
                        print("Invalid choice.")

                elif emp_option == "6":
                    break

                else:
                    print("Invalid option. Please try again.")

        elif option == "3":
            # Exit the application
            print("\nThank you for visiting Pythonccino Coffee & Book Cafe! Goodbye!\n")
            break
        else:
            print("Invalid option. Please try again.")

# Ensure `cli.py` only runs when executed directly
if __name__ == "__main__":
    main()
