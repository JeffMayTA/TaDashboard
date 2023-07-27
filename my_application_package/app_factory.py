import os
from flask import Flask, redirect, url_for, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from dotenv import load_dotenv
from flask_login import login_required, current_user, LoginManager
from google.cloud import logging as gcp_logging
from flask_mail import Mail

from .models import db, User  # import db here
from .forms import ForgotPasswordForm, ResetPasswordForm, RegisterForm  


load_dotenv()
login_manager = LoginManager()

mail = Mail()


def create_app():
    # Import the blueprints
    from .blueprints.tenadams import tenadams
    from .blueprints.auth import auth
    from .blueprints.nuvance import nuvance
    from .blueprints.admin import admin_bp
    
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    app.secret_key = os.environ.get('SECRET_KEY') or 'supersecretkey'

# Check if the app is running in production
    if os.getenv('FLASK_ENV') == 'production':
        # Use Google Cloud SQL database in production
        db_user = os.environ.get('DB_USER')
        db_pass = os.environ.get('DB_PASSWORD')
        db_name = os.environ.get('DB_NAME')
        instance_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqldb://{db_user}:{db_pass}@/{db_name}?unix_socket=/cloudsql/{instance_connection_name}'
    else:
        # Use SQLite database in development
        database_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../dash.db')
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + database_path


    db.init_app(app)
    migrate = Migrate(app, db)

        
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Set the login view
    login_manager.login_message = 'Please log in to access this page'  # Set the login message
    
    app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'apikey'
    app.config['MAIL_PASSWORD'] = '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'
    app.config['MAIL_DEFAULT_SENDER'] = 'digital@tenadams.com'
    
    mail.init_app(app)


    # Register the blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(tenadams, url_prefix='/tenadams')
    app.register_blueprint(nuvance, url_prefix='/nuvance')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    

    @app.route('/')
    @login_required  # Apply the login_required decorator
    def index():
        # Perform necessary processing or logic
        # Retrieve data if needed
        photo_url = current_user.profile_photo_url

        return render_template('index.html', photo_url=photo_url)
    
    
    
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        form = RegisterForm()
        if form.validate_on_submit():
            form.create_user()
            flash('Account created successfully. You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        return render_template('signup.html', form=form)


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
