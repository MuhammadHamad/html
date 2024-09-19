import smtplib
import imaplib
import email
from email.mime.text import MIMEText
import time
import logging
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Email configuration
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("email_automation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


def send_email(to_email, subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL
        msg['To'] = to_email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
        logging.info(f"Email sent to {to_email}")
    except smtplib.SMTPException as e:
        logging.error(f"Failed to send email: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error while sending email: {str(e)}")


def check_and_respond_to_emails():
    try:
        with imaplib.IMAP4_SSL(IMAP_SERVER) as imap:
            imap.login(EMAIL, PASSWORD)
            imap.select("INBOX")

            _, message_numbers = imap.search(None, "UNSEEN")

            for num in message_numbers[0].split():
                try:
                    _, msg_data = imap.fetch(num, "(RFC822)")
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)

                    sender = email.utils.parseaddr(email_message['From'])[1]
                    subject = email_message['Subject']

                    logging.info(f"Processing email from {
                                 sender} with subject: {subject}")

                    # Simple auto-response
                    response_subject = f"Re: {subject}"
                    response_body = f"Thank you for your email. This is an automated response."

                    send_email(sender, response_subject, response_body)

                    # Mark the email as read
                    imap.store(num, '+FLAGS', '\\Seen')
                    logging.info(
                        f"Processed and responded to email from {sender}")
                except Exception as e:
                    logging.error(
                        f"Error processing individual email: {str(e)}")
    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP error: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error while checking emails: {str(e)}")


def main():
    logging.info("Starting email automation script")
    while True:
        try:
            check_and_respond_to_emails()
        except KeyboardInterrupt:
            logging.info("Script terminated by user")
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
        time.sleep(60)  # Check for new emails every 60 seconds


if __name__ == "__main__":
    main()
