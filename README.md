# Email_Automation

This Python script allows you to automate sending emails to multiple recipients with optional attachments. It provides a command-line interface for configuring email settings, recipients, and email content.

## Features

- Send emails to multiple recipients.
- Configure email subject, message, and optional attachments.
- Manage email configuration via a JSON file.
- Logging of errors, warnings, and successes.
- Schedule email sending as a daily task.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed on your system.
- A Gmail account with less secure apps enabled (for sending emails).
- Knowledge of recipient email addresses stored in a file.

## Setup

1. Clone the repository to your local machine:

```shell
git clone https://github.com/X8Addictor/Email_Automation
```

2. Then open terimal and change the directory where the repository is cloned.
3. Copy and paste the code in terimal to install the required Python packages:
```shell
pip install -r requirements.txt
```

## Usage

1. Run the script using the following command in terminal or open and run the code in any IDE of your choice:
```shell
python email_automation.py
```

2. Follow the prompts to configure your email settings, recipients, subject, message, attachment (optional) and daily scheduled time.

## Configuration
You can edit the configuration settings in the config.json file located in the Config directory. The following fields are available:

`email_address`: Your Gmail email address. 

`recipients_file`: Path to the file containing recipient email addresses.

`subject`: Email subject.

`message`: Email message body.

`attachment_path (optional)`: Path to an attachment file.

## Schedule Task
The script allows you to schedule email sending as a daily task at user specified time.

## Logging
The script logs errors, warnings, and successes to a log file (Logs/Logs.log). You can review this log file to check the status of sent emails or troubleshoot any issues.
