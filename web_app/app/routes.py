from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import Users, OTP, Admin, db, JobApplication, Consulting, ExamApplication, JobPost, ExamPost
from .helpers import send_otp_email, hash_password, check_password, encrypt_security_answer, check_security_answer
from datetime import datetime, timedelta
import random
import bcrypt
from sqlalchemy import func
from .resume import extract_resume_text, calculate_similarity_score, skills_match_score, missing_skills
import os
import cv2
import pytesseract
import re
from werkzeug.utils import secure_filename
import numpy as np
from app.utils import extract_text_from_pdf, extract_ielts_details


# Automatically detect Tesseract path


import pytesseract


pytesseract.pytesseract.tesseract_cmd = r"C:\Users\NIHARIKA\PycharmProjects\DATA EXTRACTION\web_app\tesseract.exe"

main = Blueprint('main', __name__)
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Users.query.filter_by(email=email).first()

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
        user = Users.query.filter_by(email=email).first()
        session['user_id'] = user.id
        session.pop('signin_email', None)
        flash('Sign in successful.', 'success')
        return redirect(url_for('main.user_dashboard'))
    
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

        if Users.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('signup.html')

        # Insert into historical users table
        new_user = Users(
            name=name, email=email, password=password, mobile=mobile,
            dob=dob, security_question=security_question,
            security_answer=security_answer, city=city, state=state, country=country
        )
        db.session.add(new_user)
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

# Forgot Password
@main.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = Users.query.filter_by(email=email).first()

        if user:
            session['reset_email'] = email  # Store email in session
            session['security_question'] = user.security_question  # Store security question
            flash('Email found. Answer the security question.', 'success')
            return redirect(url_for('main.security_question'))
        else:
            flash('Email not found.', 'danger')
    return render_template('forgot_password.html')

@main.route('/security_question', methods=['GET', 'POST'])
def security_question():
    email = session.get('reset_email')
    question = session.get('security_question')

    if not email or not question:
        flash('Session expired. Please try again.', 'warning')
        return redirect(url_for('main.forgot_password'))

    if request.method == 'POST':
        answer = request.form['security_answer']
        user = Users.query.filter_by(email=email).first()

        if user and user.security_answer.lower() == answer.lower():
            otp = random.randint(100000, 999999)
            send_otp_reset(email, otp)  # Send OTP to email
            session['otp'] = otp  # Store OTP in session
            flash('Security answer correct. OTP sent to your email.', 'success')
            return redirect(url_for('main.verify_reset_otp'))
        else:
            flash('Incorrect security answer.', 'danger')

    return render_template('security_question.html', question=question)


# OTP Verification
@main.route('/verify_reset_otp', methods=['GET', 'POST'])
def verify_reset_otp():
    email = session.get('reset_email')
    otp = session.get('otp')

    if not email or not otp:
        flash('Session expired. Please try again.', 'warning')
        return redirect(url_for('main.forgot_password'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp')

        if str(otp) == entered_otp:
            flash('OTP verified. You can now reset your password.', 'success')
            return redirect(url_for('main.reset_password'))
        else:
            flash('Incorrect OTP. Please try again.', 'danger')

    return render_template('verify_reset_otp.html')


# Reset Password
@main.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')

    if not email:
        flash('Session expired. Please try again.', 'warning')
        return redirect(url_for('main.forgot_password'))

    if request.method == 'POST':
        new_password = request.form['new_password'].encode('utf-8')
        confirm_password = request.form['confirm_password'].encode('utf-8')

        if new_password == confirm_password:
            hashed_password = bcrypt.hashpw(new_password, bcrypt.gensalt())
            user = Users.query.filter_by(email=email).first()
            user.password = hashed_password.decode('utf-8')
            db.session.commit()
            flash('Password reset successful. You can now log in.', 'success')
            session.pop('reset_email', None)  # Clear session data
            session.pop('otp', None)
            session.pop('security_question', None)
            return redirect(url_for('main.signin'))
        else:
            flash('Passwords do not match.', 'danger')

    return render_template('reset_password.html')


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

admin_bp = Blueprint('admin', __name__)

@main.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('main.admin_login'))

    total_users = Users.query.count()
    total_jobs = JobPost.query.count()
    total_exams = ExamPost.query.count()
    pending_jobs = JobApplication.query.filter_by(application_status='pending').count()
    pending_exams = ExamApplication.query.filter_by(application_status='pending').count()
    pending_consulting = Consulting.query.filter_by(status='pending').count()

    return render_template('admin_dashboard.html', total_users=total_users, total_jobs=total_jobs,
                           total_exams=total_exams, pending_jobs=pending_jobs,
                           pending_exams=pending_exams, pending_consulting=pending_consulting)


@main.route('/admin/manage_users')
def manage_users():
    if 'admin' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('main.admin_login'))

    users = Users.query.all()
    return render_template('admin_manage_users.html', users=users)

@main.route('/admin/activate_user/<int:user_id>')
def activate_user(user_id):
    if 'admin' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    user = Users.query.get(user_id)
    if user:
        user.status = 'active'
        db.session.commit()
        flash(f'User {user.name} activated!', 'success')

    return redirect(url_for('main.manage_users'))

@main.route('/admin/deactivate_user/<int:user_id>')
def deactivate_user(user_id):
    if 'admin' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    user = Users.query.get(user_id)
    if user:
        user.status = 'inactive'
        db.session.commit()
        flash(f'User {user.name} deactivated!', 'warning')

    return redirect(url_for('main.manage_users'))

@main.route('/admin/manage_jobs')
def manage_jobs():
    if 'admin' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('main.admin_login'))

    jobs = JobPost.query.all()
    return render_template('admin_manage_jobs.html', jobs=jobs)

@main.route('/admin/add_job', methods=['GET', 'POST'])
def add_job():
    if 'admin' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        skills_required = request.form['skills_required']

        new_job = JobPost(title=title, description=description, skills_required=skills_required, posted_by=session['admin'])
        db.session.add(new_job)
        db.session.commit()
        flash('New job posted successfully!', 'success')

        return redirect(url_for('main.manage_jobs'))

    return render_template('admin_add_job.html')

@main.route('/admin/delete_job/<int:job_id>')
def delete_job(job_id):
    if 'admin' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    job = JobPost.query.get(job_id)
    if job:
        db.session.delete(job)
        db.session.commit()
        flash('Job deleted successfully!', 'danger')

    return redirect(url_for('main.manage_jobs'))

@main.route('/admin/manage_applications')
def manage_applications():
    if 'admin' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('main.admin_login'))

    applications = JobApplication.query.all()
    return render_template('admin_manage_applications.html', applications=applications)

@main.route('/admin/approve_application/<int:application_id>')
def approve_application(application_id):
    if 'admin' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    application = JobApplication.query.get(application_id)
    if application:
        application.application_status = 'accepted'
        db.session.commit()
        flash('Application approved!', 'success')

    return redirect(url_for('main.manage_applications'))

@main.route('/admin/reject_application/<int:application_id>')
def reject_application(application_id):
    if 'admin' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    application = JobApplication.query.get(application_id)
    if application:
        application.application_status = 'rejected'
        db.session.commit()
        flash('Application rejected!', 'danger')

    return redirect(url_for('main.manage_applications'))

@main.route('/admin/manage_consulting', methods=['GET'])
def manage_consulting():
    if 'admin' not in session:  # Ensure session key matches admin login
        flash('Admin login required!', 'danger')
        return redirect(url_for('main.admin_login'))  # ✅ Redirect to Admin Login

    try:
        # ✅ Retrieve consulting requests with only required fields
        consulting_requests = Consulting.query.with_entities(
            Consulting.id,
            Consulting.user_id,
            Consulting.passport_number,
            Consulting.center_number,
            Consulting.ielts_listening_score_user,   # ✅ Fix field name
            Consulting.ielts_listening_score_extracted,  # ✅ Fix field name
            Consulting.ielts_reading_score_user,    # ✅ Fix field name
            Consulting.ielts_reading_score_extracted, # ✅ Fix field name
            Consulting.ielts_writing_score_user,    # ✅ Fix field name
            Consulting.ielts_writing_score_extracted, # ✅ Fix field name
            Consulting.ielts_speaking_score_user,   # ✅ Fix field name
            Consulting.ielts_speaking_score_extracted, # ✅ Fix field name
            Consulting.status
        ).all()

        if not consulting_requests:
            flash('No consulting requests found!', 'info')

        return render_template('admin_manage_consulting.html', consulting_requests=consulting_requests)

    except Exception as e:
        flash(f"Error loading consulting requests: {str(e)}", "danger")
        return redirect(url_for('main.admin_dashboard'))  # ✅ Redirect to Admin Dashboard


@main.route('/admin/approve_consulting/<int:consulting_id>')
def approve_consulting(consulting_id):
    if 'admin' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    request_data = Consulting.query.get(consulting_id)
    if request_data:
        request_data.status = 'verified'
        db.session.commit()
        flash('Consulting request approved!', 'success')

    return redirect(url_for('main.manage_consulting'))

@main.route('/admin/reject_consulting/<int:consulting_id>')
def reject_consulting(consulting_id):
    if 'admin' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    request_data = Consulting.query.get(consulting_id)
    if request_data:
        request_data.status = 'discrepancy_found'
        db.session.commit()
        flash('Consulting request rejected!', 'danger')

    return redirect(url_for('main.manage_consulting'))

@main.route('/admin/manage_exams')
def manage_exams():
    if 'admin' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('main.admin_login'))

    exams = ExamPost.query.all()
    return render_template('admin_manage_exams.html', exams=exams)

@main.route('/admin/add_exam', methods=['GET', 'POST'])
def add_exam():
    if 'admin' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    if request.method == 'POST':
        exam_name = request.form['exam_name']
        description = request.form['description']

        new_exam = ExamPost(exam_name=exam_name, description=description, posted_by=session['admin'])
        db.session.add(new_exam)
        db.session.commit()
        flash('New exam added successfully!', 'success')

        return redirect(url_for('main.manage_exams'))

    return render_template('admin_add_exam.html')

@main.route('/admin/delete_exam/<int:exam_id>')
def delete_exam(exam_id):
    if 'admin' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    exam = ExamPost.query.get(exam_id)
    if exam:
        db.session.delete(exam)
        db.session.commit()
        flash('Exam deleted successfully!', 'danger')

    return redirect(url_for('main.manage_exams'))

@main.route('/admin/manage_exam_applications')
def manage_exam_applications():
    if 'admin' not in session:
        flash("Admin access required!", "warning")
        return redirect(url_for('main.admin_login'))

    applications = db.session.query(
        ExamApplication.id,
        Users.name.label("applicant_name"),
        ExamPost.exam_name,
        ExamApplication.pan_card.label("entered_pan"),
        ExamApplication.aadhar_card.label("entered_aadhar"),
        ExamApplication.extracted_pan.label("extracted_pan"),
        ExamApplication.extracted_aadhar.label("extracted_aadhar"),
        ExamApplication.application_status,
        ExamApplication.dob_matched,
        ExamApplication.id_number_matched
    ).join(Users, ExamApplication.user_id == Users.id
    ).join(ExamPost, ExamApplication.exam_id == ExamPost.id
    ).all()

    return render_template('admin_manage_exam_applications.html', applications=applications)

@main.route('/admin/update_exam_application_status/<int:application_id>', methods=['POST'])
def update_exam_application_status(application_id):
    if 'admin' not in session:
        flash("Admin access required!", "warning")
        return redirect(url_for('main.admin_login'))

    application = ExamApplication.query.get(application_id)
    if not application:
        flash("Application not found!", "danger")
        return redirect(url_for('main.manage_exam_applications'))

    new_status = request.form.get("status")
    if new_status in ["accepted", "rejected"]:
        application.application_status = new_status
        db.session.commit()
        flash(f"Application {new_status.capitalize()} successfully!", "success")
    else:
        flash("Invalid status update!", "danger")

    return redirect(url_for('main.manage_exam_applications'))



@main.route('/admin/approve_exam_application/<int:application_id>')
def approve_exam_application(application_id):
    if 'admin' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    application = ExamApplication.query.get(application_id)
    if application:
        application.application_status = 'accepted'
        db.session.commit()
        flash('Exam application approved!', 'success')

    return redirect(url_for('main.manage_exam_applications'))

@main.route('/admin/reject_exam_application/<int:application_id>')
def reject_exam_application(application_id):
    if 'admin' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_login'))

    application = ExamApplication.query.get(application_id)
    if application:
        application.application_status = 'rejected'
        db.session.commit()
        flash('Exam application rejected!', 'danger')

    return redirect(url_for('main.manage_exam_applications'))

@main.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('main.signin'))

    user_id = session['user_id']
    total_jobs_applied = JobApplication.query.filter_by(user_id=user_id).count()
    total_exams_applied = ExamApplication.query.filter_by(user_id=user_id).count()
    consulting_request = Consulting.query.filter_by(user_id=user_id).first()

    return render_template('user_dashboard.html', total_jobs_applied=total_jobs_applied,
                           total_exams_applied=total_exams_applied, consulting_request=consulting_request)

@main.route('/jobs')
def view_jobs():
    if 'user_id' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('main.signin'))

    jobs = JobPost.query.all()
    return render_template('jobs.html', jobs=jobs)

UPLOAD_FOLDER = "app/static/resumes/"
ALLOWED_EXTENSIONS = {"pdf", "docx"}

# Ensure the folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Check if the uploaded file format is allowed
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


import os
from flask import current_app

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Define upload folder (make sure this directory exists)
UPLOAD_FOLDER = os.path.join(current_app.root_path, "static/resumes")

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/apply_job/<int:job_id>', methods=['POST'])
def apply_job(job_id):
    if 'user_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('main.signin'))

    user_id = session['user_id']
    job = JobPost.query.get(job_id)

    if not job:
        flash("Job not found!", "danger")
        return redirect(url_for('main.view_jobs'))

    # Check if file is uploaded
    if 'resume' not in request.files:
        flash("No file uploaded!", "danger")
        return redirect(url_for('main.view_jobs'))

    resume_file = request.files['resume']

    if resume_file.filename == '':
        flash("No selected file!", "danger")
        return redirect(url_for('main.view_jobs'))

    # Validate file extension
    if allowed_file(resume_file.filename):
        # Save resume with a unique filename
        resume_filename = f"user_{user_id}_job_{job_id}.{resume_file.filename.split('.')[-1]}"
        resume_path = os.path.join(UPLOAD_FOLDER, resume_filename)
        resume_file.save(resume_path)

        try:
            # Extract text from resume
            resume_text = extract_resume_text(resume_path)
            print("Extracted Resume Text:", resume_text)

            # Compute Scores
            similarity = calculate_similarity_score(job.description, resume_text)  # ✅ Correct similarity calculation
            skills_score, matched_skills, additional_info = skills_match_score(job.skills_required, resume_text)  # ✅ Fix skill matching

            # Convert lists to strings for database storage
            matched_skills_str = ", ".join(matched_skills)
            additional_info_str = ", ".join(additional_info)

            # Store job application in the database
            job_application = JobApplication(
                user_id=user_id,
                job_id=job_id,
                resume=resume_filename,  # ✅ Store relative path, not full system path
                similarity_score=float(similarity),  # ✅ Convert NumPy float to standard Python float
                skills_matched=matched_skills_str,  # ✅ Convert list to string
                additional_info=additional_info_str,  # ✅ Convert list to string
                application_status="pending"
            )

            db.session.add(job_application)
            db.session.commit()

            flash("Job application submitted successfully!", "success")
            return redirect(url_for('main.user_dashboard'))

        except Exception as e:
            flash(f"Error processing resume: {str(e)}", "danger")
            return redirect(url_for('main.view_jobs'))

    else:
        flash("Invalid file format! Only PDF & DOCX are allowed.", "danger")
        return redirect(url_for('main.view_jobs'))




# Function to extract text using OCR
def extract_text_from_image(image_path):
    """Extracts text from an image using Tesseract OCR with preprocessing."""
    try:
        # Load image
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        
        # Apply Adaptive Thresholding to enhance text
        processed_img = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2
        )

        # Apply OCR
        extracted_text = pytesseract.image_to_string(processed_img, config='--psm 6', lang='eng')
        return extracted_text.strip()
    except Exception as e:
        return f"OCR Error: {str(e)}"



@main.route('/apply_exam/<int:exam_id>', methods=['GET', 'POST'])
def apply_exam(exam_id):
    if 'user_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('main.signin'))

    user_id = session['user_id']
    exam = ExamPost.query.get(exam_id)

    if not exam:
        flash("Exam not found!", "danger")
        return redirect(url_for('main.view_exams'))

    if request.method == 'GET':
        return render_template('apply_exam.html', exam=exam)

    if request.method == 'POST':
        entered_pan = request.form.get("pan_card").replace(" ", "")
        entered_aadhar = request.form.get("aadhar_card").replace(" ", "")

        # ✅ Fix: Check for uploaded files
        if 'pan_card_image' not in request.files or 'aadhar_card_image' not in request.files:
            flash("Both PAN and Aadhar images must be uploaded!", "danger")
            return render_template('apply_exam.html', exam=exam)

        pan_image = request.files['pan_card_image']
        aadhar_image = request.files['aadhar_card_image']

        if pan_image.filename == '' or aadhar_image.filename == '':
            flash("Please upload both PAN and Aadhar images!", "danger")
            return render_template('apply_exam.html', exam=exam)

        # ✅ Fix: Secure file names
        pan_filename = secure_filename(f"user_{user_id}_pan_{pan_image.filename}")
        aadhar_filename = secure_filename(f"user_{user_id}_aadhar_{aadhar_image.filename}")
        pan_path = os.path.join("uploads/", pan_filename)
        aadhar_path = os.path.join("uploads/", aadhar_filename)

        pan_image.save(pan_path)
        aadhar_image.save(aadhar_path)

        # ✅ Fix: Extract numbers from images using OCR
        extracted_pan = extract_text_from_image(pan_path)
        extracted_aadhar = extract_text_from_image(aadhar_path)

        # ✅ Define this function before calling it
        def extract_number_from_text(text, doc_type):
            """
            Extracts PAN (10-character alphanumeric) or Aadhar (12-digit) from OCR text.
            """
            if doc_type == "pan":
                match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text)  # PAN Pattern
            elif doc_type == "aadhar":
                match = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', text)  # Aadhar Pattern (with or without spaces)
            else:
                match = None  # Invalid type

            return match.group(0).replace(" ", "") if match else "OCR Failed"  # Remove spaces for Aadhar

        # ✅ Now call the function correctly
        extracted_pan_number = extract_number_from_text(extracted_pan, "pan")  # ✅ Fixed call
        extracted_aadhar_number = extract_number_from_text(extracted_aadhar, "aadhar")  # ✅ Fixed call

        # ✅ Fix: Compare extracted vs entered values
        id_match = (entered_pan == extracted_pan_number) and (entered_aadhar == extracted_aadhar_number)

        # ✅ Fix: Save to DB
        exam_application = ExamApplication(
            user_id=user_id,
            exam_id=exam_id,
            pan_card=entered_pan,
            aadhar_card=entered_aadhar,
            extracted_pan=extracted_pan_number if extracted_pan_number else "OCR Failed",
            extracted_aadhar=extracted_aadhar_number if extracted_aadhar_number else "OCR Failed",
            dob_matched=False,
            id_number_matched=id_match,
            application_status="pending"
        )

        db.session.add(exam_application)
        db.session.commit()

        flash("Exam application submitted successfully!", "success")
        return redirect(url_for('main.user_dashboard'))


@main.route('/exams')
def view_exams():
    if 'user_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('main.signin'))

    exams = ExamPost.query.all()
    return render_template('exams.html', exams=exams)


@main.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('main.signin'))

    user = Users.query.get(session['user_id'])

    if request.method == 'POST':
        user.name = request.form['name']
        user.mobile = request.form['mobile']
        user.dob = request.form['dob']
        user.city = request.form['city']
        user.state = request.form['state']
        user.country = request.form['country']
        user.security_question = request.form['security_question']
        user.security_answer = request.form['security_answer']

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))

    return render_template('profile.html', user=user)

import os
import re
from flask import request, redirect, url_for, render_template, flash, session
from werkzeug.utils import secure_filename
from app import db
from app.models import Consulting
#from app.utils import extract_text_from_image  # OCR Extraction Function
import os

UPLOAD_FOLDER = "static/uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


import os
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from app import db
from app.models import Consulting
from app.utils import extract_text_from_pdf, extract_ielts_details

@main.route('/consulting_request', methods=['GET', 'POST'])
def consulting_request():
    if 'user_id' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('main.signin'))

    user_id = session['user_id']
    consulting_request = Consulting.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        print("Received POST request!")
        print("Form Data:", request.form)

        # ✅ Get user-entered values
        passport_number = request.form.get('passport_number', "").strip()
        center_number = request.form.get('center_number', "").strip()
        listening_score = float(request.form.get('ielts_listening_score_user', "0").strip())
        reading_score = float(request.form.get('ielts_reading_score_user', "0").strip())
        writing_score = float(request.form.get('ielts_writing_score_user', "0").strip())
        speaking_score = float(request.form.get('ielts_speaking_score_user', "0").strip())

        # ✅ Handle file upload
        uploaded_ielts = request.files.get('uploaded_ielts')
        ielts_path = None

        extracted_data = {
            "passport_number": "OCR Failed",
            "center_number": "OCR Failed",
            "listening": "OCR Failed",
            "reading": "OCR Failed",
            "writing": "OCR Failed",
            "speaking": "OCR Failed",
        }

        if uploaded_ielts and uploaded_ielts.filename:
            ielts_filename = secure_filename(f"user_{user_id}_ielts_{uploaded_ielts.filename}")
            ielts_path = os.path.join("static/uploads/", ielts_filename)
            uploaded_ielts.save(ielts_path)

            extracted_text = extract_text_from_pdf(ielts_path)
            extracted_data = extract_ielts_details(extracted_text)

        # ✅ Compare extracted values with user-entered values
        passport_match = passport_number == extracted_data["passport_number"]
        center_match = center_number == extracted_data["center_number"]
        listening_match = listening_score == float(extracted_data["listening"])
        reading_match = reading_score == float(extracted_data["reading"])
        writing_match = writing_score == float(extracted_data["writing"])
        speaking_match = speaking_score == float(extracted_data["speaking"])

        if consulting_request:
            consulting_request.passport_number = passport_number
            consulting_request.center_number = center_number
            consulting_request.ielts_listening_score_user = listening_score
            consulting_request.ielts_reading_score_user = reading_score
            consulting_request.ielts_writing_score_user = writing_score
            consulting_request.ielts_speaking_score_user = speaking_score
            consulting_request.uploaded_ielts = ielts_path

            # OCR Data
            consulting_request.extracted_passport_number = extracted_data["passport_number"]
            consulting_request.extracted_center_number = extracted_data["center_number"]
            consulting_request.ielts_listening_score_extracted = extracted_data["listening"]
            consulting_request.ielts_reading_score_extracted = extracted_data["reading"]
            consulting_request.ielts_writing_score_extracted = extracted_data["writing"]
            consulting_request.ielts_speaking_score_extracted = extracted_data["speaking"]

            # Match Results
            consulting_request.passport_match = passport_match
            consulting_request.center_match = center_match
            consulting_request.listening_match = listening_match
            consulting_request.reading_match = reading_match
            consulting_request.writing_match = writing_match
            consulting_request.speaking_match = speaking_match

        else:
            consulting_request = Consulting(
                user_id=user_id,
                passport_number=passport_number,
                center_number=center_number,
                ielts_listening_score_user=listening_score,
                ielts_reading_score_user=reading_score,
                ielts_writing_score_user=writing_score,
                ielts_speaking_score_user=speaking_score,
                uploaded_ielts=ielts_path,
            )

            db.session.add(consulting_request)

        db.session.commit()
        flash('Consulting request updated successfully!', 'success')
        return redirect(url_for('main.consulting_request'))

    return render_template('consulting_request.html', consulting_request=consulting_request)

@main.route('/my_jobs')
def my_jobs():
    if 'user_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('main.signin'))

    user_id = session['user_id']
    
    # Fetch job applications with job details
    job_applications = db.session.query(JobApplication, JobPost).join(JobPost, JobApplication.job_id == JobPost.id).filter(JobApplication.user_id == user_id).all()

    return render_template('my_jobs.html', job_applications=job_applications)

@main.route('/my_exams')
def my_exams():
    if 'user_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('main.signin'))

    user_id = session['user_id']

    # ✅ FIX: Join `ExamApplication` with `ExamPost` to fetch exam details
    applications = db.session.query(
        ExamApplication.id,
        ExamPost.exam_name,
        ExamApplication.application_status,
        ExamApplication.applied_at,
        ExamApplication.pan_card.label("entered_pan"),
        ExamApplication.extracted_pan.label("extracted_pan"),
        ExamApplication.aadhar_card.label("entered_aadhar"),
        ExamApplication.extracted_aadhar.label("extracted_aadhar"),
        ExamApplication.dob_matched,
        ExamApplication.id_number_matched
    ).join(ExamPost, ExamApplication.exam_id == ExamPost.id
    ).filter(ExamApplication.user_id == user_id).all()

    return render_template('my_exams.html', applications=applications)

@main.route('/my_consulting')
def my_consulting():
    if 'user_id' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('main.signin'))

    user_id = session['user_id']
    consulting_request = Consulting.query.filter_by(user_id=user_id).first()

    return render_template('my_consulting.html', consulting_request=consulting_request)



@main.route('/approve_job/<int:application_id>')
def approve_job(application_id):
    if 'admin' not in session:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main.admin_login'))

    application = JobApplication.query.get(application_id)
    if application:
        application.application_status = "accepted"
        db.session.commit()
        flash("Job application approved!", "success")

    return redirect(url_for('main.manage_jobs'))

@main.route('/reject_job/<int:application_id>')
def reject_job(application_id):
    if 'admin' not in session:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main.admin_login'))

    application = JobApplication.query.get(application_id)
    if application:
        application.application_status = "rejected"
        db.session.commit()
        flash("Job application rejected!", "danger")

    return redirect(url_for('main.manage_jobs'))

@main.route('/admin/manage_job_applications')
def manage_job_applications():
    if 'admin' not in session:
        flash("Admin access required!", "warning")
        return redirect(url_for('main.admin_login'))

    job_applications = db.session.query(
        JobApplication.id,
        Users.name.label("applicant_name"),
        JobPost.title.label("job_title"),
        JobApplication.similarity_score,
        JobApplication.skills_matched,
        JobApplication.additional_info,
        JobApplication.application_status
    ).join(Users, JobApplication.user_id == Users.id
    ).join(JobPost, JobApplication.job_id == JobPost.id
    ).all()

    return render_template('admin_manage_job_applications.html', job_applications=job_applications)

@main.route('/admin/update_application_status/<int:application_id>', methods=['POST'])
def update_application_status(application_id):
    if 'admin' not in session:
        flash("Admin access required!", "warning")
        return redirect(url_for('main.admin_login'))

    new_status = request.form.get('status')
    application = JobApplication.query.get(application_id)

    if application:
        application.application_status = new_status
        db.session.commit()
        flash(f"Application {new_status} successfully!", "success")
    else:
        flash("Application not found!", "danger")

    return redirect(url_for('main.manage_job_applications'))

@main.route('/apply_consulting', methods=['GET', 'POST'])
def apply_consulting():
    if 'user_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('main.signin'))

    user_id = session['user_id']

    if request.method == 'GET':
        return render_template('apply_consulting.html')

    if request.method == 'POST':
        # ✅ **Get Entered Values**
        entered_center_number = request.form.get("center_number")
        entered_test_date = request.form.get("test_date")
        entered_dob = request.form.get("dob")
        entered_family_name = request.form.get("family_name")
        entered_first_name = request.form.get("first_name")
        entered_listening_score = request.form.get("listening_score")
        entered_reading_score = request.form.get("reading_score")
        entered_writing_score = request.form.get("writing_score")
        entered_speaking_score = request.form.get("speaking_score")
        entered_overall_band_score = request.form.get("overall_band_score")
        entered_cefr_level = request.form.get("cefr_level")

        # ✅ **Check for Uploaded Files**
        if 'ielts_scorecard' not in request.files or 'gre_scorecard' not in request.files:
            flash("Both IELTS and GRE scorecards must be uploaded!", "danger")
            return render_template('apply_consulting.html')

        ielts_file = request.files['ielts_scorecard']
        gre_file = request.files['gre_scorecard']

        if ielts_file.filename == '' or gre_file.filename == '':
            flash("Please upload both IELTS and GRE scorecards!", "danger")
            return render_template('apply_consulting.html')

        # ✅ **Secure and Save Uploaded Files**
        ielts_filename = secure_filename(f"user_{user_id}_ielts_{ielts_file.filename}")
        gre_filename = secure_filename(f"user_{user_id}_gre_{gre_file.filename}")
        ielts_path = os.path.join("uploads/", ielts_filename)
        gre_path = os.path.join("uploads/", gre_filename)

        ielts_file.save(ielts_path)
        gre_file.save(gre_path)

        # ✅ **Process IELTS & GRE Scorecards**
        ielts_text = process_scorecard(ielts_path)  # Uses PDF + OCR processing
        gre_text = process_scorecard(gre_path)  # Uses PDF + OCR processing

        # ✅ **Extract Scores**
        ielts_scores = extract_ielts_scores(ielts_text)
        gre_scores = extract_gre_scores(gre_text)

        # ✅ **Compare Extracted vs. Entered**
        score_mismatch = []
        if ielts_scores["Center Number"] and ielts_scores["Center Number"] != entered_center_number:
            score_mismatch.append("Center Number Mismatch")
        if ielts_scores["Test Date"] and ielts_scores["Test Date"] != entered_test_date:
            score_mismatch.append("Test Date Mismatch")
        if ielts_scores["Date of Birth"] and ielts_scores["Date of Birth"] != entered_dob:
            score_mismatch.append("Date of Birth Mismatch")

        # ✅ **Save Consulting Request**
        consulting_application = Consulting(
            user_id=user_id,
            ielts_date=entered_test_date,
            ielts_expiry=None,
            ielts_listening_score=entered_listening_score,
            ielts_reading_score=entered_reading_score,
            ielts_writing_score=entered_writing_score,
            ielts_speaking_score=entered_speaking_score,
            gre_date=gre_scores["Test Date"],
            gre_expiry=None,
            gre_verbal_score=gre_scores["Verbal Reasoning Scaled Score"],
            gre_quantitative_score=gre_scores["Quantitative Reasoning Scaled Score"],
            gre_awa_score=gre_scores["Analytical Writing Score"],
            uploaded_ielts=ielts_path,
            uploaded_gre=gre_path,
            status="pending",
            name_matched=True,  # Assuming names matched for now
            dob_matched=ielts_scores["Date of Birth"] == entered_dob,
            score_mismatch=", ".join(score_mismatch) if score_mismatch else None
        )

        db.session.add(consulting_application)
        db.session.commit()

        flash("Consulting application submitted successfully!", "success")
        return redirect(url_for('main.user_dashboard'))
