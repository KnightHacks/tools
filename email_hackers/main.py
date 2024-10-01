# ========================
# Questions? Email me (dany)
# root <at> ucf <dot> edu
#
# if no response
# email knighthacks infra team
# infra <at> knighthacks <dot> org
# ========================

import sys
import argparse
import smtplib
import traceback
import logging
from typing import List, NoReturn, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up logging
try:
    logging.basicConfig(filename='email_sender.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
except Exception as e:
    print(f"Error setting up logging: {e}")
    sys.exit(1)

def format_exception_info(Exception: type, inst: Exception, maxTBlevel: int = 5) -> None:
    """
    Neatly format exceptions that are raised.

    This function formats exception information and writes it to the log file.

    Args:
        Exception (type): The exception class.
        inst (Exception): The instance of the exception that occurred.
        maxTBlevel (int, optional): The maximum number of traceback levels to include. Defaults to 5.

    Returns:
        None
    """
    try:
        buffer: str = ''
        error_details: List[str] = []

        cla, exc, trbk = sys.exc_info()
        excName: str = cla.__name__
        try:
            excArgs: Any = exc.__dict__['args']
        except KeyError:
            excArgs: str = '<no args>'
        excTb: List[str] = traceback.format_tb(trbk, maxTBlevel)

        nice_msg_buffer: str = ('ERROR\n' + 
           ' '.ljust(35, ' ') +  '-----' + '\n'+ 
           ' '.ljust(35, ' ') + 
            'Type: '.ljust(10, " ") + excName + '\n'+ 
           ' '.ljust(35, ' ') + 
            'Args: '.ljust(10, " ") + str(excArgs) + '\n'+ 
           ' '.ljust(35, ' ') + 
            'Details: '.ljust(10, " ") + str(inst)) + '\n'

        raw_string: str = str(excTb).strip('[]')
        buffer_list: List[str] = raw_string.split(',')
            
        for item in buffer_list:
            item = item.replace('\\n', ' ')   
            item = item.replace("'", '')
            item = item.strip(' ')
            nice_msg_buffer = nice_msg_buffer + ' '.ljust(40, ' ') + item + '\n'
        
        write_log("ERROR", nice_msg_buffer)
    except Exception as e:
        print(f"Error in format_exception_info: {e}")

def write_log(type: str, message: object) -> None:
    """
    Write a log message to the log file.

    This function simplifies writing to the log file by handling different log levels.

    Args:
        type (str): The type of log message (INFO, DEBUG, WARNING, ERROR, CRITICAL, or LINE).
        message (object): The message to be logged.

    Returns:
        None
    """
    try:
        message: str = str(message)

        if 'INFO' == type:
            logging.info(message)
        elif 'DEBUG' == type:
            logging.debug(message)
        elif 'WARNING' == type:
            logging.warning(message)
        elif 'ERROR' == type:
            logging.error(message)
        elif 'CRITICAL' == type:
            logging.critical(message)
        elif 'LINE' == type:
            logging.info('=' * 80)
    except Exception as e:
        print(f"Error writing to log: {e}")

def read_email_list(file_path: str) -> Optional[List[str]]:
    """
    Read a list of email addresses from a file.

    This function reads a file and returns a list of non-empty, stripped lines.

    Args:
        file_path (str): The path to the file containing email addresses.

    Returns:
        Optional[List[str]]: A list of email addresses read from the file, or None if an error occurs.
    """
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        format_exception_info(Exception, e)
        write_log("ERROR", f"Error reading email list from {file_path}: {e}")
        return None

def send_email(sender_email: str, sender_password: str, recipient_email: str, subject: str, body: str) -> bool:
    """
    Send an email using SMTP.

    This function creates and sends an email to a single recipient.

    Args:
        sender_email (str): The email address of the sender.
        sender_password (str): The password for the sender's email account.
        recipient_email (str): The email address of the recipient.
        subject (str): The subject line of the email.
        body (str): The body content of the email.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    try:
        message: MIMEMultipart = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        write_log("INFO", f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        format_exception_info(Exception, e)
        write_log("ERROR", f"Error sending email to {recipient_email}: {e}")
        return False

def main() -> NoReturn:
    """
    Main function to send emails to confirmed and accepted lists.

    This function parses command-line arguments, reads email lists from files,
    and sends emails to addresses in those lists.

    Args:
        None

    Returns:
        NoReturn: This function either completes successfully or exits the program.

    Raises:
        SystemExit: If there's an unhandled exception, the program exits with status code 1.
    """
    try:
        parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Send emails to confirmed and accepted lists.")
        parser.add_argument("email", help="Sender's email address")
        parser.add_argument("password", help="Sender's email password")
        parser.add_argument("confirmed_list", help="Path to the confirmed list file")
        parser.add_argument("accepted_list", help="Path to the accepted list file")
        args: argparse.Namespace = parser.parse_args()

        confirmed_emails: Optional[List[str]] = read_email_list(args.confirmed_list)
        accepted_emails: Optional[List[str]] = read_email_list(args.accepted_list)

        if confirmed_emails is None or accepted_emails is None:
            write_log("ERROR", "Failed to read email lists. Exiting.")
            sys.exit(1)

        # Email content for confirmed list
        confirmed_subject: str = "Confirmation Email"
        confirmed_body: str = "This is the email for the confirmed list."

        # Email content for accepted list
        accepted_subject: str = "Acceptance Email"
        accepted_body: str = "This is the email for the accepted list."

        # Send emails to confirmed list
        for email in confirmed_emails:
            if send_email(args.email, args.password, email, confirmed_subject, confirmed_body):
                write_log("INFO", f"Sent confirmation email to {email}")
            else:
                write_log("WARNING", f"Failed to send confirmation email to {email}")

        # Send emails to accepted list
        for email in accepted_emails:
            if send_email(args.email, args.password, email, accepted_subject, accepted_body):
                write_log("INFO", f"Sent acceptance email to {email}")
            else:
                write_log("WARNING", f"Failed to send acceptance email to {email}")

        write_log("INFO", "Email sending process completed")
    except Exception as e:
        format_exception_info(Exception, e)
        write_log("CRITICAL", "Unhandled exception in main function. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        format_exception_info(Exception, e)
        sys.exit(1)