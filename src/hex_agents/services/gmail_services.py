import smtplib
from email.message import EmailMessage
from typing import Optional


class GmailService:
    def __init__(self, sender_email: str, app_password: str):
        """Initializes the Gmail service with credentials.
        
        Args:
            sender_email (str): Your full Gmail address.
            app_password (str): The Google Account App Password (16 characters).
        """
        self.sender_email = sender_email
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        cc: Optional[str] = None
    ) -> bool:
        """Sends an email using Gmail's SMTP SSL server.
        
        Args:
            to_email (str): The recipient's email address.
            subject (str): The subject line of the email.
            body (str): The text content/body of the email.
            cc (str, optional): Carbon copy recipient email address.
            
        Returns:
            bool: True if sent successfully, raises an exception otherwise.
        """
        try:
            # Construct the email message
            msg = EmailMessage()
            msg.set_content(body)
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = to_email
            
            if cc:
                msg["Cc"] = cc

            # Connect and send securely via SSL
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.app_password)
                server.send_message(msg)
                
            return True

        except Exception as e:
            raise e


# # --- Example Usage ---
# if __name__ == "__main__":
#     # Replace these with your actual credentials and test details
#     SENDER = "mspoudel92@gmail.com"
#     APP_PWD = "dwib iemx nsob ifqs"
    
#     # Initialize the service
#     mailer = GmailService(sender_email=SENDER, app_password=APP_PWD)
    
#     # Send an email
#     mailer.send_email(
#         to_email="mnsh6313@gmail.com",
#         subject="Hello from your Python Class!",
#         body="This is an automated test email sent using the GmailService class."
#     )