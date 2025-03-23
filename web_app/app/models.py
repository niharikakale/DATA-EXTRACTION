from datetime import datetime, timedelta
from . import db

# Admin Model
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# OTP Verification Model
class OTP(db.Model):
    __tablename__ = 'otp'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10))

# User Model
class Users(db.Model):
    __tablename__ = 'users'
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

# Job Posting Model
class JobPost(db.Model):
    __tablename__ = 'job_posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills_required = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.Integer, db.ForeignKey('admin.id', ondelete='SET NULL'))
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

# Job Applications Model
class JobApplication(db.Model):
    __tablename__ = 'job_applications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    job_id = db.Column(db.Integer, db.ForeignKey('job_posts.id', ondelete='CASCADE'))
    resume = db.Column(db.String(255), nullable=False)
    similarity_score = db.Column(db.Float)
    skills_matched = db.Column(db.Text)
    additional_info = db.Column(db.Text)
    application_status = db.Column(db.Enum('pending', 'reviewed', 'accepted', 'rejected'), default='pending')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

# Consulting Model
from app import db

from app import db

from app import db

class Consulting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    passport_number = db.Column(db.String(20), nullable=False)
    extracted_passport_number = db.Column(db.String(20), nullable=True)

    center_number = db.Column(db.String(20), nullable=False)
    extracted_center_number = db.Column(db.String(20), nullable=True)

    test_date = db.Column(db.Date, nullable=False)
    dob = db.Column(db.Date, nullable=False)

    ielts_listening_score_user = db.Column(db.Float, nullable=False)
    ielts_listening_score_extracted = db.Column(db.Float, nullable=True)

    ielts_reading_score_user = db.Column(db.Float, nullable=False)
    ielts_reading_score_extracted = db.Column(db.Float, nullable=True)

    ielts_writing_score_user = db.Column(db.Float, nullable=False)
    ielts_writing_score_extracted = db.Column(db.Float, nullable=True)

    ielts_speaking_score_user = db.Column(db.Float, nullable=False)
    ielts_speaking_score_extracted = db.Column(db.Float, nullable=True)

    uploaded_ielts = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum('pending', 'verified', 'discrepancy_found'), default='pending')

    passport_match = db.Column(db.Boolean, default=False)
    center_match = db.Column(db.Boolean, default=False)
    listening_match = db.Column(db.Boolean, default=False)
    reading_match = db.Column(db.Boolean, default=False)
    writing_match = db.Column(db.Boolean, default=False)
    speaking_match = db.Column(db.Boolean, default=False)

# Competitive Exams Model
class ExamPost(db.Model):
    __tablename__ = 'exam_posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.Integer, db.ForeignKey('admin.id', ondelete='SET NULL'))
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

class ExamApplication(db.Model):
    __tablename__ = 'exam_applications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    exam_id = db.Column(db.Integer, db.ForeignKey('exam_posts.id', ondelete='CASCADE'))
    pan_card = db.Column(db.String(255), nullable=False)  # User-entered PAN
    aadhar_card = db.Column(db.String(255), nullable=False)  # User-entered Aadhar
    extracted_pan = db.Column(db.String(255), nullable=True)  # Extracted PAN from OCR
    extracted_aadhar = db.Column(db.String(255), nullable=True)  # Extracted Aadhar from OCR
    dob_matched = db.Column(db.Boolean, default=False)  # Flag for DOB match
    id_number_matched = db.Column(db.Boolean, default=False)  # Flag for ID match
    application_status = db.Column(db.Enum('pending', 'reviewed', 'accepted', 'rejected'), default='pending')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

# Admin Logs Model
class AdminLog(db.Model):
    __tablename__ = 'admin_logs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id', ondelete='CASCADE'))
    action = db.Column(db.Text, nullable=False)
    action_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize Database
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()