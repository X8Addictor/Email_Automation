import smtplib
import ssl
import json
import os
import re
import logging
from getpass import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Define constants for file paths and directories.
FILE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIRECTORY = os.path.join(FILE_DIRECTORY, 'Config')
os.makedirs(CONFIG_DIRECTORY, exist_ok=True)
CONFIG_FILE = os.path.join(CONFIG_DIRECTORY, 'config.json')
LOG_DIRECTORY = os.path.join(FILE_DIRECTORY, 'Logs')
os.makedirs(LOG_DIRECTORY, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIRECTORY, 'Logs.log')

# Flags for controlling the printing of warnings and errors.
error_flag = True
warning_flag = True

def setup_logging():
    """Configure logging settings to save logs to a file."""
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

def get_recipients(filename):
    """
    Read recipient email addresses from a file and validate their format.

    Args:
        filename (str): The path to the file containing recipient email addresses.

    Returns:
        list: A list of valid recipient email addresses.
        None: If no valid email addresses are found.
    
     Raises:
        FileNotFoundError: If the recipients file is not found.
        Exception: If an unexpected error occurs during processing.
    """
    try:
        recipient_addresses = []
        
        with open(filename, 'r') as recipients_file:
            for line in recipients_file:
                recipient = check_email_format(line.strip())
                if recipient:
                    recipient_addresses.append(recipient)
                else:
                    log_warning(f'Invalid email "{line.strip()}" in "{filename}".')

        if not recipient_addresses:
            raise Exception(f'No valid email address(s) found in "{filename}".')

        return recipient_addresses
    except FileNotFoundError:
        log_error(f'Recipients file "{recipients_file}" not found.\n')
        return None
    except Exception as e:
        log_error(f'{e}\n')
        return None

def check_email_format(email_address):
    """
    Check if an email address has a valid format.

    Args:
        email_address (str): The email address to validate.

    Returns:
        str: The valid email address.
        None: If the email address format is invalid.
    """
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,3}$'

    if re.match(email_pattern, email_address):
        return email_address

def send_email(sender_address, sender_password, recipient_addresses, subject, message, attachment_path = ''):
    """
    Send an email to multiple recipients with optional attachments.

    Args:
        sender_address (str): The sender's email address.
        sender_password (str): The sender's email password.
        recipient_addresses (list): A list of recipient email addresses.
        subject (str): The email subject.
        message (str): The email body text.
        attachment_path (str, optional): Path to an attachment file (default is None).

    Returns:
        bool: True if the email was sent successfully, False otherwise.

    Raises:
        Exception: If an unexpected error occurs during email sending.
    """
    try:
        if not sender_address and not sender_password:
            raise Exception(f'No email address and password found in "{CONFIG_FILE}".')

        if not check_email_format(sender_address):
            raise Exception(f'Invalid gmail address format "{sender_address}", please edit the gmail address format in "{CONFIG_FILE}".')

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as gmail_server:
            gmail_server.login(gmail_address, gmail_password)

            for recipient_address in recipient_addresses:
                msg = compose_email(sender, recipient, subject, message, attachment_path)

                if msg is not None:
                    server.sendmail(sender, recipient, message.as_string())
                    log_success(f'Successfully sent email to "{recipient_address.strip()}"\n')

        return True
    except Exception as e:
        log_error(f'{e}\n')
        return False
        
def compose_email(email_address, recipient_address, subject, message, attachment_path = ''):
    """
    Compose an email message with optional attachments.

    Args:
        email_address (str): The sender's email address.
        recipient_address (str): The recipient's email address.
        subject (str): The email subject.
        message (str): The email body text.
        attachment_path (str, optional): Path to an attachment file (default is None).

    Returns:
        email.message.Message: The composed email message.
        None: If an attachment file is specified but not found.

    Raises:
        FileExistsError: If the specified attachment file does not exist.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = recipient_address
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        if os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as attachment_file:
                part = MIMEApplication(attachment_file.read(), Name=os.path.basename(attachment_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                msg.attach(part)
        elif not os.path.exists(attachment_path) and attachment_path is not '':
            raise FileExistsError

        return msg
    except FileExistsError:
        log_error(f'Attachment file "{attachment_path}" not found.\n')
        return None

def log_warning(message):
    """
    Log a warning message and print it to the console.

    Args:
        message (str): The warning message.
    """
    global warning_flag

    if warning_flag:
        print(f'Warning: Invalid email address(es) found "{filename}", check "{LOG_FILE}" for more info.')
        warning_flag = False

    logging.warning(message)    

def log_error(message):
    """
    Log an error message and print it to the console.

    Args:
        message (str): The error message.
    """
    global error_flag

    if error_flag:
        print(f'Error(s) occured, please check "{LOG_FILE}" for more details.')
        error_flag = False

    logging.error(message)

def log_success(message):
    """
    Log a success message.

    Args:
        message (str): The success message.
    """
    logging.info(message)

def main(email_address, email_password, recipients_file, subject, message, attachment_path = ''):
    """
    Main function to send emails to recipients.

    Args:
        email_address (str): The sender's email address.
        email_password (str): The sender's email password.
        recipients_file (str): Path to the file containing recipient email addresses.
        subject (str): The email subject.
        message (str): The email body text.
        attachment_path (str, optional): Path to an attachment file (default is None).
    """
    recipient_email_addresses = get_recipients(recipients_file)

    if recipient_email_addresses:
        success = send_email(email_address, email_password, recipient_email_addresses, subject, message, attachment_path)


if __name__ == '__main__':
    setup_logging()

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    email_address = config.get('email_address', '')
    email_password = config.get('email_password', '')
    recipients_file = config.get('recipients_file', '')
    subject = config.get('subject', '')
    message = config.get('message', '')
    attachment_path = config.get('attachment_path')  # This can be empty

    main(email_address, email_password, recipients_file, subject, message, attachment_path)