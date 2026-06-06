import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


class SMTPClient:
    """
    A unified, Object-Oriented client for dispatching emails.
    Handles SMTP connection and MIME formatting.
    """
    def __init__(self, server: str = None, port: int = None, user: str = None, password: str = None):
        self.server = server or os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        self.port = port or int(os.environ.get("SMTP_PORT", 587))
        self.user = user or os.environ.get("SMTP_USER")
        self.password = password or os.environ.get("SMTP_PASS")
        
        if not self.user or not self.password:
            logging.warning("SMTP credentials missing. Email dispatch will fail.")

    def send_email(self, subject: str, body_html: str, recipient: str = None) -> bool:
        """
        Dispatches an HTML email to the recipient.
        """
        target_email = recipient or os.environ.get("ALERT_EMAIL")
        
        if not all([self.user, self.password, target_email]):
            logging.error("Missing required credentials/recipient. Cannot send email.")
            return False
            
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.user
            msg['To'] = target_email
            
            part = MIMEText(body_html, 'html')
            msg.attach(part)
            
            server = smtplib.SMTP(self.server, self.port)
            server.starttls()
            server.login(self.user, self.password)
            server.sendmail(self.user, target_email, msg.as_string())
            server.quit()
            
            logging.info(f"Email successfully dispatched to {target_email}")
            return True
        except Exception as e:
            logging.error(f"SMTP delivery failed: {e}")
            return False
