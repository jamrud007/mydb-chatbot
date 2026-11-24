
import sys
import os
import logging

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils.email_sender import EmailSender

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email():
    print("Testing SMTP Configuration...")
    print(f"SMTP Server: {Config.SMTP_SERVER}:{Config.SMTP_PORT}")
    print(f"Sender Email: {Config.SMTP_EMAIL}")
    
    if Config.SMTP_EMAIL == 'your_email@gmail.com' or Config.SMTP_PASSWORD == 'your_app_password_here':
        print("❌ Error: Default credentials detected. Please update .env file.")
        return

    # Send to self
    success = EmailSender.send_verification_email(Config.SMTP_EMAIL, "TEST-123")
    
    if success:
        print("\n✅ Email Verification Sent Successfully!")
        print(f"Check the inbox of {Config.SMTP_EMAIL} for a code 'TEST-123'.")
    else:
        print("\n❌ Failed to send email. Check your App Password and Internet Connection.")

if __name__ == "__main__":
    test_email()
