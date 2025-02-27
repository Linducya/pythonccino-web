from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

# # Access and execute functions from routes.py
# from app.routes import home
# print(home())

# from app.cli import main

# if __name__ == '__main__':
#     main()
