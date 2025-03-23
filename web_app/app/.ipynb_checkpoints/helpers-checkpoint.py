import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import bcrypt

def send_email(to_email, subject, body):
    sender_email = "smartverify2025@gmail.com"
    sender_password = "rytgfaawcjukpztk"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_otp_email(to_email, otp, purpose):
    subject_map = {
        'signin': "Your OTP to sign in",
        'signup': "Your OTP for account creation",
        'reset': "Your OTP to reset your password"
    }
    subject = subject_map.get(purpose, "Your OTP")
    body = f"Your OTP is {otp}. This OTP is valid for 10 minutes."
    return send_email(to_email, subject, body)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def encrypt_security_answer(answer):
    return bcrypt.hashpw(answer.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_security_answer(answer, hashed_answer):
    return bcrypt.checkpw(answer.encode('utf-8'), hashed_answer.encode('utf-8'))
