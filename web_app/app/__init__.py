from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URI',
        'mysql+pymysql://root:root@localhost/extraction'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
    app.config['SESSION_TYPE'] = 'filesystem'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)

    # Import and register Blueprints
    with app.app_context():
        from .routes import main
        #from .admin_routes import admin_bp  # Make sure this file exists

        app.register_blueprint(main)  # Main routes
        #app.register_blueprint(admin_bp, url_prefix='/admin')  # Admin routes

    return app
