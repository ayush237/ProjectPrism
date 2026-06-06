import argparse
import logging
from utils.email_client import SMTPClient

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class EmailDispatchTask:
    """
    Orchestrates the parsing of command line arguments and dispatching of notification emails.
    """
    def __init__(self):
        self.smtp_client = SMTPClient()
        
    def execute(self):
        parser = argparse.ArgumentParser(description="Dispatch Notification Emails")
        parser.add_argument("--subject", required=True, help="Subject line of the email")
        parser.add_argument("--body-file", required=True, help="Path to the file containing the HTML/Markdown body")
        parser.add_argument("--to", help="Optional recipient email override")
        
        args = parser.parse_args()
        
        try:
            with open(args.body_file, 'r', encoding='utf-8') as f:
                body_content = f.read()
                
            self.smtp_client.send_email(args.subject, body_content, args.to)
        except FileNotFoundError:
            logging.error(f"Could not find body file at {args.body_file}")

if __name__ == "__main__":
    task = EmailDispatchTask()
    task.execute()
