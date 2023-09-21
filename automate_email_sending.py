import smtplib
import ssl
import json
import os
import re
import logging
import schedule
import time
from getpass import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Define constants for file paths and directories.
FILE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIRECTORY = os.path.join(FILE_DIRECTORY, 'Config')
CONFIG_FILE = os.path.join(CONFIG_DIRECTORY, 'config.json')
os.makedirs(CONFIG_DIRECTORY, exist_ok=True)
LOG_DIRECTORY = os.path.join(FILE_DIRECTORY, 'Logs')
LOG_FILE = os.path.join(LOG_DIRECTORY, 'Logs.log')
os.makedirs(LOG_DIRECTORY, exist_ok=True)

# Flags for controlling the printing of warnings and errors.
error_flag = True
warning_flag = True

def setup_logging():
    """Configure logging settings to save logs to a file."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as log_file:
            log_file.write('')
    
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def load_config():
    """
    Load the configuration from the JSON file or create a new configuration if not found.

    This function checks if the configuration JSON file exists. If it exists, it attempts to load the configuration
    from the file. If the file is missing or if any required configuration fields are absent, it invokes the 
    `setup_config()` function to create and initialize a new configuration. If the JSON file is corrupted, it logs
    an error and returns an empty dictionary.

    Returns:
        dict: The loaded or created configuration as a dictionary.

    Raises:
        json.JSONDecodeError: If there is an issue with decoding the JSON file.
        Exception: If an unexpected error during process. 
    """
    try:
        if not os.path.exists(CONFIG_FILE):
            config = setup_config({})
        else:
            config = read_config_file()

            required_fields = ['email_address', 'recipients_file', 'subject', 'message']
            missing_fields = [field for field in required_fields if field not in config]

            if missing_fields:
                config = setup_config(config)

        return config
    except json.JSONDecodeError as e:
        log_error(f'Error decoding JSON in configuration file: {str(e)}')
        return {}
    except Exception as e:
        log_error(f'{e}\n')
        return {}

def setup_config(config):
    """
    Load or create a configuration JSON file, prompt the user for missing values, and update the JSON file.

    This function checks if specific keys are present in the configuration JSON file. If any of these keys are missing,
    the user is prompted to enter the missing values. The updated configuration is then saved to the JSON file.

    Returns:
        dict: The updated configuration as a dictionary.
    """
    try:
        write_config_file(config)

        config_keys = [
            ('email_address', 'Enter your email address: '),
            ('recipients_file', 'Enter the recipients file path: '),
            ('subject', 'Enter the email subject: '),
            ('message', 'Enter the email message/body: '),
            ('attachment_path', 'Enter the file attachment path (optional, press Enter to skip): ')
        ]

        for key, prompt in config_keys:
            if not config.get(key):
                value = input(prompt)
                config[key] = value

                
        write_config_file(config)
        config = read_config_file() 

        return config
    except Exception as e:
        raise e

def read_config_file():
    """
    Read and load the configuration from the JSON file.

    Returns:
        dict: The loaded configuration as a dictionary.

    Raises:
        json.JSONDecodeError: If there is an issue with decoding the JSON file.
    """
    try:
        with open(CONFIG_FILE, 'r') as config_file:
            config = json.load(config_file)  

        return config
    except json.JSONDecodeError as e:
        raise e
        return {}

def write_config_file(config):
    """
    Write the configuration to the JSON file.

    Args:
        config (dict): The configuration to be written to the JSON file.

    Raises:
        Exception: If an unexpected error occurs during writing.
    """
    try:
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file, indent=4)
    except Exception as e:
        raise e

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
            raise Exception(f'No valid email address(es) found in "{filename}".')

        return recipient_addresses
    except FileNotFoundError:
        log_error(f'Recipients file "{filename}" not found.\n')
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
        attachment_path (str, optional): Path to an attachment file (default is '').

    Returns:
        bool: True if the email was sent successfully, False otherwise.

    Raises:
        Exception: If an unexpected error occurs during email sending.
    """
    try:
        if not check_email_format(sender_address):
            raise Exception(f'Invalid gmail address format "{sender_address}", please edit the correct gmail address format in "{CONFIG_FILE}".')

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as gmail_server:
            gmail_server.login(sender_address, sender_password)

            for recipient_address in recipient_addresses:
                msg = compose_email(sender_address, recipient_address, subject, message, attachment_path)

                if msg is not None:
                    #gmail_server.sendmail(sender_address, recipient_address, msg.as_string())
                    log_success(f'Successfully sent email to "{recipient_address.strip()}"\n')

        return True
    except FileExistsError as e:
        log_error(f'{e}\n')
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
        elif not os.path.exists(attachment_path) and attachment_path != '':
            raise FileExistsError(f'Attachment file "{attachment_path}" not found.')

        return msg
    except FileExistsError as e:
        raise e

def log_warning(message):
    """
    Log a warning message and print it to the console.

    Args:
        message (str): The warning message.
    """
    global warning_flag

    if warning_flag:
        print(f'Warning: Invalid email address(es) found, check "{LOG_FILE}" for more info.')
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

    if recipient_email_addresses is not None:
        success = send_email(email_address, email_password, recipient_email_addresses, subject, message, attachment_path)

        if success:
            print('Successfully sent emails.')
        else:
            print('Failed to send emails.')

def my_scheduled_task():
    """
    Schedule and run a daily task at 9:00 AM using the 'schedule' library.

    This function schedules the 'main' function to run daily at 9:00 AM and enters
    an infinite loop to continuously check for pending scheduled tasks and run them.
    It handles a KeyboardInterrupt (Ctrl+C) gracefully by printing an exit message.

    Note:
    - The scheduled task will run indefinitely until manually interrupted.
    """
    schedule.every().day.at("09:00").do(main)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print('Script exiting...')
    finally:
        pass

if __name__ == '__main__':
    setup_logging()
    config = load_config()

    email_address = config.get('email_address', '')
    email_password = os.getenv('EMAIL_PASSWORD')

    if not email_password:
        email_password = getpass('Enter your email password: ')

    recipients_file = config.get('recipients_file', '')
    subject = config.get('subject', '')
    message = config.get('message', '')
    attachment_path = config.get('attachment_path')

    main(email_address, email_password, recipients_file, subject, message, attachment_path)

    #my_scheduled_task()