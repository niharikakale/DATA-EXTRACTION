#from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from . import db
# Initialize SQLAlchemy
#db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10))

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prediction_type = db.Column(db.String(50), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('completed', 'failed'), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    security_question = db.Column(db.String(255), nullable=False)
    security_answer = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='inactive')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)

class Book(db.Model):
    __tablename__ = 'books'  # Ensure correct table name
    ISBN = db.Column(db.String(20), primary_key=True)
    book_title = db.Column(db.String(255), nullable=False)  # Correct field name
    book_author = db.Column(db.String(255), nullable=False)  # Correct field name
    year_of_publication = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100), nullable=False)

class Rating(db.Model):
    __tablename__ = 'ratings'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    ISBN = db.Column(db.String(20), db.ForeignKey('books.ISBN', ondelete='CASCADE'), primary_key=True)
    book_rating = db.Column(db.Integer, nullable=True)

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    user_ref_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Initialize Models
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()