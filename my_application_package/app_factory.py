import os
from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_login import login_required, current_user, LoginManager
from google.cloud import logging as gcp_logging

from .models import db, User  # import db here

load_dotenv()
login_manager = LoginManager()

def create_app():
    # Import the blueprints
    from .blueprints.tenadams import tenadams
    from .blueprints.auth import auth
    
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    app.secret_key = os.environ.get('SECRET_KEY') or 'supersecretkey'

    database_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../dash.db')
    database_uri = 'sqlite:///' + database_path
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Set the login view
    login_manager.login_message = 'Please log in to access this page'  # Set the login message

    # Register the blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(tenadams, url_prefix='/tenadams')
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    @login_required  # Apply the login_required decorator
    def index():
        # Perform necessary processing or logic
        # Retrieve data if needed
        return render_template('index.html')

    # Define your custom error handler
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    if os.environ.get('FLASK_ENV') != 'development':
        # Instantiate a Google Cloud client
        client = gcp_logging.Client()

        # Connects the logger to the root logging handler; by default this captures
        # all logs at INFO level and higher
        client.setup_logging()


    return app
