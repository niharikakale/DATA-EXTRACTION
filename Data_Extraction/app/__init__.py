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
        'mysql+pymysql://root:root@localhost/book_recommendation'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
    app.config['SESSION_TYPE'] = 'filesystem'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)

    # Register models after db.init_app()
    with app.app_context():
        from .models import User, Book, Rating, Admin, Prediction, OTP, Users
        from .routes import main
        from .content_based_filtering import content_bp  # Import the content-based filtering blueprint
        from .collaborative_filtering import collaborative_bp
        from .popularity_filtering import popularity_bp
        from .mood_filtering import mood_bp

        app.register_blueprint(main)
        app.register_blueprint(content_bp, url_prefix="/content")
        app.register_blueprint(collaborative_bp, url_prefix="/collaborative")
        app.register_blueprint(popularity_bp, url_prefix="/popularity")
        app.register_blueprint(mood_bp, url_prefix="/mood")

        db.create_all()

    @app.context_processor
    def inject_user():
        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
        return dict(user=user)

    return app
