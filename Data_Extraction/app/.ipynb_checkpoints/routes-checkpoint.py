from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import User, OTP, Admin, db, Prediction, Book, Rating, Users
from .helpers import send_otp_email, hash_password, check_password, encrypt_security_answer, check_security_answer
from datetime import datetime, timedelta
import random
import bcrypt
from sqlalchemy import func
import pandas as pd
from .mood_filtering import recommend_books

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Email not registered.', 'danger')
            return render_template('signin.html')

        if not check_password(password, user.password):
            flash('Incorrect password.', 'danger')
            return render_template('signin.html')

        if user.status == 'inactive':
            flash('Waiting for admin approval.', 'warning')
            return render_template('signin.html')

        otp = random.randint(100000, 999999)
        otp_entry = OTP.query.filter_by(email=email).first()
        if otp_entry:
            otp_entry.otp = otp
            otp_entry.created_at = datetime.utcnow()
        else:
            new_otp = OTP(email=email, otp=str(otp))
            db.session.add(new_otp)

        db.session.commit()
        send_otp_email(email, otp, 'signin')
        session['signin_email'] = email
        flash('OTP sent to your email.', 'success')
        return redirect(url_for('main.verify_signin_otp'))
    
    return render_template('signin.html')

@main.route('/verify_signin_otp', methods=['GET', 'POST'])
def verify_signin_otp():
    email = session.get('signin_email')
    if not email:
        return redirect(url_for('main.signin'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        otp_entry = OTP.query.filter_by(email=email).first()

        if not otp_entry or otp_entry.otp != entered_otp:
            flash('Incorrect or expired OTP.', 'danger')
            return render_template('verify_signin_otp.html')

        db.session.delete(otp_entry)
        db.session.commit()
        user = User.query.filter_by(email=email).first()
        session['user_id'] = user.id
        session.pop('signin_email', None)
        flash('Sign in successful.', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('verify_signin_otp.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = hash_password(request.form['password'])
        mobile = request.form['mobile']
        dob = request.form['dob']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        security_question = request.form['security_question']
        security_answer = encrypt_security_answer(request.form['security_answer'])

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('signup.html')

        # Insert into historical users table
        new_user = User(
            name=name, email=email, password=password, mobile=mobile,
            dob=dob, security_question=security_question,
            security_answer=security_answer, city=city, state=state, country=country
        )
        db.session.add(new_user)
        db.session.commit()

        # Insert into active users table for recommendation system
        new_users_entry = Users(
            user_id=new_user.id,  # Use the newly created user ID
            location=f"{city}, {state}, {country}",
            age=(datetime.utcnow().year - int(dob[:4])),
            city=city, state=state, country=country,
            user_ref_id=new_user.id  # Ensure user_ref_id is set
        )
        db.session.add(new_users_entry)
        db.session.commit()

        otp = random.randint(100000, 999999)
        session['signup_data'] = {
            'name': name, 'email': email, 'password': password, 'mobile': mobile,
            'dob': dob, 'security_question': security_question, 'security_answer': security_answer, 'otp': otp
        }
        send_otp_email(email, otp, 'signup')
        flash('OTP sent to your email for verification.', 'success')
        return redirect(url_for('main.verify_signup_otp'))
    
    return render_template('signup.html')


@main.route('/verify_signup_otp', methods=['GET', 'POST'])
def verify_signup_otp():
    signup_data = session.get('signup_data')
    if not signup_data:
        return redirect(url_for('main.signup'))

    if request.method == 'POST':
        entered_otp = request.form['otp']
        if str(signup_data['otp']) != entered_otp:
            flash('Incorrect OTP. Please try again.', 'danger')
            return render_template('verify_signup_otp.html')

        new_user = User(**{k: v for k, v in signup_data.items() if k != 'otp'})
        db.session.add(new_user)
        db.session.commit()
        session.pop('signup_data', None)
        flash('Account created successfully. Waiting for admin approval.', 'success')
        return redirect(url_for('main.signin'))
    
    return render_template('verify_signup_otp.html')

@main.route("/dashboard", methods=["GET"])
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for("main.signin"))

    user_id = session["user_id"]

    # Fetch user's ratings
    rated_books = (
        db.session.query(Book.book_title, Book.book_author, Book.genre, Rating.book_rating)
        .join(Rating, Book.ISBN == Rating.ISBN)
        .filter(Rating.user_id == user_id)
        .all()
    )

    rated_books_df = pd.DataFrame(rated_books, columns=["Title", "Author", "Genre", "Your Rating"])

    # Get Mood-Based Recommendations
    selected_mood = session.get("last_mood", "Happy")  # Use last selected mood if available
    recommendations = recommend_books(selected_mood, top_n=5)

    return render_template(
        "dashboard.html",
        recommendations=recommendations,
        rated_books=rated_books_df
    )


# Admin Login
@main.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        admin_user = Admin.query.filter_by(username=username).first()

        if admin_user and bcrypt.checkpw(password, admin_user.password.encode('utf-8')):
            session['admin'] = admin_user.id
            flash('Welcome Admin!', 'success')
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('admin_login.html')

@main.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('main.admin_login'))

    # Data for total users by status
    active_users = User.query.filter_by(status='active').count()
    inactive_users = User.query.filter_by(status='inactive').count()
    archived_users = User.query.filter_by(status='archived').count()
    deleted_users = User.query.filter_by(status='deleted').count()

    # Top 5 users by prediction count
    top_users = db.session.query(
        User.name, db.func.count(Prediction.id).label('predictions')
    ).join(Prediction).group_by(User.id).order_by(db.desc('predictions')).limit(5).all()

    top_users_data = {
        "labels": [user.name for user in top_users],
        "values": [user.predictions for user in top_users],
    }
    print("Top Users Data:", top_users_data)
    

    # Predictions by type
    prediction_counts = db.session.query(
        Prediction.prediction_type, db.func.count(Prediction.id)
    ).group_by(Prediction.prediction_type).all()

    prediction_data = {
        "labels": [prediction[0] for prediction in prediction_counts],
        "values": [prediction[1] for prediction in prediction_counts],
    }
    print("Prediction Data:", prediction_data)

    return render_template(
        'admin_dashboard.html',
        active_users=active_users,
        inactive_users=inactive_users,
        archived_users=archived_users,
        deleted_users=deleted_users,
        top_users_data=top_users_data,
        prediction_data=prediction_data,
    )

# Manage Users
@main.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    if not session.get('admin'):
        return redirect(url_for('main.admin_login'))

    users = User.query.all()

    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)

        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('main.manage_users'))

        if action == 'archive':
            user.status = 'archived'
            db.session.commit()
            flash(f'User {user.name} archived.', 'warning')
        elif action == 'activate':
            user.status = 'active'
            db.session.commit()
            flash(f'User {user.name} activated.', 'success')
        elif action == 'delete':
            db.session.delete(user)
            db.session.commit()
            flash(f'User {user.name} deleted.', 'danger')

    return render_template('manage_users.html', users=users)

import csv
from io import StringIO
from flask import Response

@main.route('/download_prediction_history')
def download_prediction_history():
    if not session.get('admin'):
        flash("You must be logged in as admin to download the prediction history.", "danger")
        return redirect(url_for('main.admin_login'))

    # Query prediction data
    predictions = db.session.query(
        Prediction.id, User.name, Prediction.prediction_type,
        Prediction.input_data, Prediction.result, Prediction.created_at
    ).join(User).all()

    # Create a CSV file in memory
    si = StringIO()
    writer = csv.writer(si)
    # Write the header row
    writer.writerow(['ID', 'User', 'Type', 'Input', 'Result', 'Date'])
    # Write the data rows
    for prediction in predictions:
        writer.writerow([prediction.id, prediction.name, prediction.prediction_type, 
                         prediction.input_data, prediction.result, prediction.created_at])

    # Generate the response
    output = Response(si.getvalue(), mimetype='text/csv')
    output.headers['Content-Disposition'] = 'attachment; filename=prediction_history.csv'
    return output

# Prediction History
@main.route('/prediction_history')
def prediction_history():
    if not session.get('admin'):
        return redirect(url_for('main.admin_login'))

    predictions = db.session.query(
        Prediction.id, User.name, Prediction.prediction_type,
        Prediction.input_data, Prediction.result, Prediction.created_at
    ).join(User).all()

    return render_template('prediction_history.html', predictions=predictions)

@main.route('/logout')
def logout():
    # Handle user logout
    if 'user_id' in session:
        session.pop('user_id', None)  # Clear user session
        flash('You have been logged out.', 'success')
        return redirect(url_for('main.signin'))

    # Handle admin logout
    if 'admin' in session:
        session.pop('admin', None)  # Clear admin session
        flash('Admin has been logged out.', 'success')
        return redirect(url_for('main.admin_login'))

    # Fallback for unauthorized access to logout
    flash('You are not logged in.', 'info')
    return redirect(url_for('main.index'))

# Books Recommendation Code

@main.route('/browse_books')
def browse_books():
    search_query = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = 40  # Number of books per page

    # Query books from database, ordered alphabetically
    books_query = Book.query.order_by(Book.book_title)

    # Apply search filter if present
    if search_query:
        books_query = books_query.filter(Book.book_title.ilike(f"%{search_query}%"))

    # Apply pagination
    books_pagination = books_query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('browse_books.html', books=books_pagination, search_query=search_query)

@main.route('/book/<isbn>', methods=['GET', 'POST'])
def book_details(isbn):
    if 'user_id' not in session:
        flash("Please log in to view book details.", "warning")
        return redirect(url_for('main.signin'))

    user_id = session['user_id']
    book = Book.query.filter_by(ISBN=isbn).first_or_404()

    # Verify if user exists in `users` table
    active_user = Users.query.filter_by(user_id=user_id).first()
    if not active_user:
        flash("User not found in recommendation system. Please re-register.", "danger")
        return redirect(url_for('main.signin'))

    # Get rating statistics (count for each rating from 1 to 10)
    rating_stats = db.session.query(
        Rating.book_rating, func.count(Rating.book_rating)
    ).filter(Rating.ISBN == isbn).group_by(Rating.book_rating).all()

    # Convert to dictionary
    rating_data = {rating: count for rating, count in rating_stats}

    # Get total rating count
    total_ratings = sum(rating_data.values())

    # Check if the user has already rated the book
    user_rating = Rating.query.filter_by(user_id=user_id, ISBN=isbn).first()

    if request.method == "POST":
        new_rating = int(request.form.get("rating"))
        
        if user_rating:
            user_rating.book_rating = new_rating  # Update rating
        else:
            new_rating_entry = Rating(user_id=user_id, ISBN=isbn, book_rating=new_rating)
            db.session.add(new_rating_entry)
        
        db.session.commit()
        flash("Your rating has been saved!", "success")
        return redirect(url_for('main.book_details', isbn=isbn))

    return render_template(
        "book_details.html", book=book, rating_data=rating_data, total_ratings=total_ratings, user_rating=user_rating
    )

