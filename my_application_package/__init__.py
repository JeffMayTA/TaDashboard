from flask import Flask
from .blueprints.auth import auth as auth_blueprint
from .blueprints.tenadams import tenadams as tenadams_blueprint

def create_app():
    app = Flask(__name__)

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(tenadams_blueprint)

    return app
