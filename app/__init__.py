from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import and register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
    
# from flask import Flask

# app = Flask(__name__,template_folder='/templates/')

# # Ensure the templates folder is correctly set (this is the default behavior)
# app.template_folder = 'templates'

# # Import routes to register them with the app
# from app import routes
