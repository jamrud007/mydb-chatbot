
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from config import Config

logger = logging.getLogger(__name__)

class EmailSender:
    """Helper class to send emails via SMTP"""
    
    @staticmethod
    def send_verification_email(to_email: str, otp_code: str) -> bool:
        """
        Send OTP verification email
        
        Args:
            to_email: Recipient email address
            otp_code: The OTP verification code
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        sender_email = Config.SMTP_EMAIL
        sender_password = Config.SMTP_PASSWORD
        
        if not sender_email or not sender_password:
            logger.error("SMTP credentials not configured")
            return False
            
        try:
            # Create message
            msg = MIMEMultipart()
            
            # Use display name if configured, otherwise just email
            display_name = Config.SMTP_DISPLAY_NAME if hasattr(Config, 'SMTP_DISPLAY_NAME') and Config.SMTP_DISPLAY_NAME else None
            if display_name:
                msg['From'] = f'"{display_name}" <{sender_email}>'
            else:
                msg['From'] = sender_email
                
            msg['To'] = to_email
            msg['Subject'] = "Kode Verifikasi MyDB Chatbot"
            
            body = f"""
            <html>
                <body>
                    <h2>Verifikasi Email Anda</h2>
                    <p>Terima kasih telah mendaftar.</p>
                    <p>Kode verifikasi Anda adalah:</p>
                    <h1 style="color: #4CAF50;">{otp_code}</h1>
                    <p>Jangan berikan kode ini kepada siapa pun.</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
            server.starttls()
            server.login(sender_email, sender_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(sender_email, to_email, text)
            server.quit()
            
            logger.info(f"Verification email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
