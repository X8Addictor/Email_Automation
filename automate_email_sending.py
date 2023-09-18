''' You work at a company that sends daily reports to clients via email. The goal of this project is to automate the process of sending these reports via email.

    Here are the steps you can take to automate this process:

    Use the smtplib library to connect to the email server and send the emails.

    Use the email library to compose the email, including the recipient's email address, the subject, and the body of the email.

    Use the os library to access the report files that need to be sent.

    Use a for loop to iterate through the list of recipients and send the email and attachment.

    Use the schedule library to schedule the script to run daily at a specific time.

    You can also set up a log file to keep track of the emails that have been sent and any errors that may have occurred during the email sending process. '''

import smtplib
import ssl
from getpass import getpass
import os
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def get_recipients(filename):
    try:
        recipient_addresses = []

        with open(filename, 'r') as recipients_file:
            for line in recipients_file:
                recipient = sanitize_email(line.strip())
                if recipient:
                    recipient_addresses.append(recipient)

        return recipient_addresses
    except FileNotFoundError:
        print('Error: File not found.')
        return []

def sanitize_email(email_address):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    if re.match(email_pattern, email_address):
        return email_address
    else:
        with open('invalid_email_addresses.log', 'a') as log_file:
            log_file.write(f'Invalid email: {email_address}\n')
        return None

def send_email(email_address, email_password, recipient_addresses, subject, message, attachment_path = None):
    try:
        # if not email_address and not email_password:
        #     raise Exception('Invalid email address or password.')

        gmail_address = sanitize_email(email_address)
        gmail_password = email_password

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as gmail_server:
            gmail_server.login(gmail_address, gmail_password)

            for recipient in recipient_addresses:
                msg = compose_email(gmail_address, recipient, subject, message, attachment_path)
                gmail_server.sendmail(gmail_address, recipient, msg.as_string())

        return True
    except Exception as e:
        print(f'Error: {e}')
        return False
        
def compose_email(email_address, recipient_address, subject, message, attachment_path = None):
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient_address
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    if attachment_path:
        with open(attachment_path, 'rb') as attachment_file:
            part = MIMEApplication(attachment_file.read(), Name=os.path.basename(attachment_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            msg.attach(part)

    return msg

def main():
    # email_address = input('Enter email address: ')
    # email_password = getpass('Enter email password: ')
    # recipients_file = input('Enter the filepath of recipients: ')
    # subject = input('Enter the email subject: ')
    # message = input('Enter the email message/body: ')
    # attachment_path = input('Enter file attachment path (optional): ')

    email_address = 'beastdemonkiller@gmail.com'
    email_password = 'karan2480'
    recipients_file = r'D:\Code Projects\Python Projects\Assignments\Week 2\Advanced\recipients.txt'
    subject = 'Test Subject'
    message = 'This is a test email'
    attachment_path = 'none'

    recipient_email_addresses = get_recipients(recipients_file)

    success = send_email(email_address, email_password, recipient_email_addresses, subject, message, attachment_path)

if __name__ == '__main__':
    main()