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


def format_exception_info(
    Exception: type,
    inst: Exception,
    maxTBlevel: int = 5
        ) -> None:
    """
    Neatly format exceptions that are raised.

    This function formats exception information and writes it to the log file.

    Args:
        Exception (type): The exception class.
        inst (Exception): The instance of the exception that occurred.
        maxTBlevel (int, optional):
            The maximum number of traceback levels to include. Defaults to 5.

    Returns:
        None
    """
    try:
        # buffer: str = ''
        # error_details: List[str] = []

        cla, exc, trbk = sys.exc_info()
        excName: str = cla.__name__
        try:
            excArgs: Any = exc.__dict__['args']
        except KeyError:
            excArgs: str = '<no args>'
        excTb: List[str] = traceback.format_tb(trbk, maxTBlevel)

        nice_msg_buffer: str = ('ERROR\n' +
                                ' '.ljust(35, ' ') + '-----' + '\n' +
                                ' '.ljust(35, ' ') +
                                'Type: '.ljust(10, " ") + excName + '\n' +
                                ' '.ljust(35, ' ') +
                                'Args: '.ljust(10, " ") + str(excArgs) + '\n' +
                                ' '.ljust(35, ' ') +
                                'Details: '.ljust(10, " ") + str(inst)) + '\n'

        raw_string: str = str(excTb).strip('[]')
        buffer_list: List[str] = raw_string.split(',')

        for item in buffer_list:
            item = item.replace('\\n', ' ')
            item = item.replace("'", '')
            item = item.strip(' ')
            nice_msg_buffer = nice_msg_buffer + ' '.ljust(
                40, ' ') + item + '\n'

        write_log("ERROR", nice_msg_buffer)
    except Exception as e:
        print(f"Error in format_exception_info: {e}")


def write_log(type: str, message: object) -> None:
    """
    Write a log message to the log file.

    This function simplifies writing to the log file,
    by handling different log levels.

    Args:
        type (str): The type of log message,
            (INFO, DEBUG, WARNING, ERROR, CRITICAL, or LINE).
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
        Optional[List[str]]:
            A list of email addresses read from the file,
            or None if an error occurs.
    """
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        format_exception_info(Exception, e)
        write_log("ERROR", f"Error reading email list from {file_path}: {e}")
        return None


def send_email(sender_email: str, sender_password: str,
               recipient_email: str, subject: str, body: str) -> bool:
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
        message.attach(MIMEText(body, 'html'))

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
        NoReturn: This function either
            completes successfully or exits the program.

    Raises:
        SystemExit: If there's an unhandled exception,
            the program exits with status code 1.
    """
    try:
        parser: argparse.ArgumentParser = argparse.ArgumentParser(
            description="Send emails to confirmed and accepted lists.")
        parser.add_argument("email", help="Sender's email address")
        parser.add_argument("password", help="Sender's email password")
        parser.add_argument(
            "confirmed_list", help="Path to the confirmed list file")
        parser.add_argument(
            "accepted_list", help="Path to the accepted list file")
        args: argparse.Namespace = parser.parse_args()

        confirmed_emails: Optional[List[str]] = read_email_list(
            args.confirmed_list)
        accepted_emails: Optional[List[str]] = read_email_list(
            args.accepted_list)

        if confirmed_emails is None or accepted_emails is None:
            write_log("ERROR", "Failed to read email lists. Exiting.")
            sys.exit(1)

        # Email content for confirmed list
        confirmed_subject: str = "See you this Friday at KnightHacks!"
        confirmed_body: str = """
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><!--$-->
            <html dir="ltr" lang="en">

            <head>
                <meta content="text/html; charset=UTF-8" http-equiv="Content-Type" />
                <meta name="x-apple-disable-message-reformatting" />
            </head>
            <div style="display:none;overflow:hidden;line-height:1px;opacity:0;max-height:0;max-width:0">🎉 We can&#x27;t wait to see you this Friday at Knight Hacks!<div> ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿</div>
            </div>

            <body style="background-color:rgb(246,249,252);background-image:url(&#x27;https://storage.googleapis.com/knighthacks-email/background%20(6).png&#x27;);background-size:cover;background-repeat:no-repeat;font-family:ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, Roboto, &quot;Helvetica Neue&quot;, Arial, &quot;Noto Sans&quot;, sans-serif, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, &quot;Segoe UI Symbol&quot;, &quot;Noto Color Emoji&quot;;margin:0px;padding:0px">
                <table align="center" width="100%" border="0" cellPadding="0" cellSpacing="0" role="presentation" style="margin-top:2rem;margin-bottom:2rem;margin-left:auto;margin-right:auto;width:600px;background-color:rgb(255,255,255);box-shadow:0 0 #0000, 0 0 #0000, 0 10px 15px -3px rgb(0,0,0,0.1), 0 4px 6px -4px rgb(0,0,0,0.1);padding-top:0px;padding-left:1.25rem;padding-right:1.25rem;padding-bottom:0px;position:relative;max-width:37.5em">
                <tbody>
                    <tr style="width:100%">
                    <td>
                        <table cellPadding="0" cellSpacing="0" width="100%">
                        <tr>
                            <td align="center" style="padding-bottom:10px">
                            <table cellPadding="0" cellSpacing="0">
                                <tr>
                                <td style="height:60px"></td>
                                </tr>
                                <tr>
                                <td align="center"><img alt="Knight Hacks Mascot" height="120" src="https://storage.googleapis.com/knighthacks-email/lenny%20(1).png" style="display:block;outline:none;border:none;text-decoration:none" width="120" /></td>
                                </tr>
                            </table>
                            </td>
                        </tr>
                        </table>
                        <h1 style="font-size:2.25rem;line-height:1.25;font-weight:700;color:rgb(28,86,153);text-align:center;margin-top:2rem;padding-left:1rem;padding-right:1rem;margin-bottom:0.625rem">We can&#x27;t wait to see you at Knight Hacks this Friday!</h1>
                        <h1 style="font-size:1.5rem;line-height:1.25;font-weight:500;padding-left:1rem;padding-right:1rem;color:rgb(71,130,198);text-align:center;margin:0px;margin-bottom:1.25rem">If you&#x27;re seeing this email, your attendance has been confirmed and you are all set to attend Knight Hacks 2024.</h1>
                        <p style="font-size:1.125rem;line-height:1.625;text-align:center;color:rgb(55,65,81);margin-bottom:1.5rem;margin:16px 0">Check-in will be running in the UCF Engineering 2 Atrium beginning at 5:30pm until 7:30. Make sure to bring an ID and a device with Discord installed to check-in.</p>
                        <table align="center" width="100%" border="0" cellPadding="0" cellSpacing="0" role="presentation" style="margin-top:-0px">
                        <tbody>
                            <tr>
                            <td>
                                <table cellPadding="0" cellSpacing="0" border="0" width="100%">
                                <tr>
                                    <td align="right" style="padding-top:20px"><img alt="Pirate Knight" src="https://storage.googleapis.com/knighthacks-email/tk.png" style="display:block;outline:none;border:none;text-decoration:none" width="150" /></td>
                                </tr>
                                </table>
                                <table cellPadding="0" cellSpacing="0" border="0" width="100%" style="margin-top:-8rem;background-color:#f0f7ff">
                                <tr>
                                    <td align="center" style="padding-top:30px;padding-bottom:24px">
                                    <h1 style="font-size:1.5rem;line-height:1.25;font-weight:700;color:rgb(28,86,153);text-align:center">Essential Resources</h1>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                    <table cellPadding="0" cellSpacing="0" border="0" width="100%">
                                        <tr>
                                        <td width="50%" align="center" valign="top" style="padding-bottom:30px"><a href="https://knight-hacks.notion.site/Hackers-Guide-Knight-Hacks-VII-9e103bd7de114151887e0da523076ecd" style="text-decoration-line:none;text-align:center;display:inline-block;background-color:rgb(28,86,153);color:rgb(255,255,255);padding-left:1rem;padding-right:1rem;border-radius:0.375rem;text-decoration:none" target="_blank">
                                            <p style="font-size:1.125rem;line-height:1.75rem;color:rgb(255,255,255);font-weight:600;display:block;margin:16px 0">Hacker&#x27;s Guide</p>
                                            </a></td>
                                        <td width="50%" align="center" valign="top" style="padding-bottom:30px"><a href="https://2024.knighthacks.org" style="text-decoration-line:none;text-align:center;display:inline-block;background-color:rgb(28,86,153);color:rgb(255,255,255);padding-left:1rem;padding-right:1rem;border-radius:0.375rem;text-decoration:none" target="_blank">
                                            <p style="font-size:1.125rem;line-height:1.75rem;color:rgb(255,255,255);font-weight:600;display:block;margin:16px 0">Official Website</p>
                                            </a></td>
                                        </tr>
                                    </table>
                                    </td>
                                </tr>
                                </table>
                            </td>
                            </tr>
                        </tbody>
                        </table>
                        <table align="center" width="100%" border="0" cellPadding="0" cellSpacing="0" role="presentation" style="background-color:rgb(28,86,153);padding:1.25rem;text-align:center">
                        <tbody>
                            <tr>
                            <td>
                                <p class="my-1.25" style="font-size:0.875rem;line-height:1.25rem;color:rgb(255,255,255);margin:16px 0">Questions? Reach out to us at<!-- --> <a href="mailto:team@knighthacks.org" style="color:rgb(255,215,0);text-decoration-line:underline;text-decoration:none" target="_blank">hackteam@knighthacks.org</a></p>
                                <p class="my-1.25" style="font-size:0.875rem;line-height:1.25rem;color:rgb(255,255,255);margin:16px 0">We can&#x27;t wait to see what you&#x27;ll create at Knight Hacks 2024!</p>
                            </td>
                            </tr>
                        </tbody>
                        </table>
                    </td>
                    </tr>
                </tbody>
                </table>
            </body>

            </html><!--/$-->
        """

        # Email content for accepted list
        accepted_subject: str = "Your Knight Hacks Status: Withdrawn"
        accepted_body: str = """
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><!--$-->
            <html dir="ltr" lang="en">

            <head>
                <meta content="text/html; charset=UTF-8" http-equiv="Content-Type" />
                <meta name="x-apple-disable-message-reformatting" />
            </head>
            <div style="display:none;overflow:hidden;line-height:1px;opacity:0;max-height:0;max-width:0">Update to your Knight Hacks Status: Withdrawn<div> ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿ ‌​‍‎‏﻿</div>
            </div>

            <body style="background-color:rgb(246,249,252);background-image:url(&#x27;https://storage.googleapis.com/knighthacks-email/background%20(6).png&#x27;);background-size:cover;background-repeat:no-repeat;font-family:ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, Roboto, &quot;Helvetica Neue&quot;, Arial, &quot;Noto Sans&quot;, sans-serif, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;, &quot;Segoe UI Symbol&quot;, &quot;Noto Color Emoji&quot;;margin:0px;padding:0px">
                <table align="center" width="100%" border="0" cellPadding="0" cellSpacing="0" role="presentation" style="margin-top:2rem;margin-bottom:2rem;margin-left:auto;margin-right:auto;width:600px;background-color:rgb(255,255,255);box-shadow:0 0 #0000, 0 0 #0000, 0 10px 15px -3px rgb(0,0,0,0.1), 0 4px 6px -4px rgb(0,0,0,0.1);padding-top:0px;padding-left:1.25rem;padding-right:1.25rem;padding-bottom:0px;position:relative;max-width:37.5em">
                <tbody>
                    <tr style="width:100%">
                    <td>
                        <table cellPadding="0" cellSpacing="0" width="100%">
                        <tr>
                            <td align="center" style="padding-bottom:10px">
                            <table cellPadding="0" cellSpacing="0">
                                <tr>
                                <td style="height:60px"></td>
                                </tr>
                                <tr>
                                <td align="center"><img alt="Knight Hacks Mascot" height="120" src="https://storage.googleapis.com/knighthacks-email/lenny%20(1).png" style="display:block;outline:none;border:none;text-decoration:none" width="120" /></td>
                                </tr>
                            </table>
                            </td>
                        </tr>
                        </table>
                        <h1 style="font-size:2.25rem;line-height:1.25;font-weight:700;color:rgb(28,86,153);text-align:center;margin-top:2rem;padding-left:1rem;padding-right:1rem;margin-bottom:0.625rem">Your Knight Hacks Status: Withdrawn</h1>
                        <h1 style="font-size:1.5rem;line-height:1.25;font-weight:500;padding-left:1rem;padding-right:1rem;color:rgb(71,130,198);text-align:center;margin:0px;margin-bottom:1.25rem">If you&#x27;re seeing this email, you did not confirm your acceptance to Knight Hacks 2024, and our ship has sailed without you.</h1>
                        <p style="font-size:1.125rem;line-height:1.625;text-align:center;color:rgb(55,65,81);margin-bottom:1.5rem;margin:16px 0">Unfortunately, we will not be able to accommodate you at Knight Hacks 2024. We sent out multiple reminders to confirm your spot on our Discord and via social media, and we&#x27;re sorry to see you go.<!-- --> <br /><br />This decision is final, and we will not be able to accommodate any further requests to attend Knight Hacks 2024. We hope to see you at future events!</p>
                        <table align="center" width="100%" border="0" cellPadding="0" cellSpacing="0" role="presentation" style="background-color:rgb(28,86,153);padding:1.25rem;text-align:center">
                        <tbody>
                            <tr>
                            <td>
                                <p class="my-1.25" style="font-size:0.875rem;line-height:1.25rem;color:rgb(255,255,255);margin:16px 0">Questions? Reach out to us at<!-- --> <a href="mailto:team@knighthacks.org" style="color:rgb(255,215,0);text-decoration-line:underline;text-decoration:none" target="_blank">hackteam@knighthacks.org</a></p>
                            </td>
                            </tr>
                        </tbody>
                        </table>
                    </td>
                    </tr>
                </tbody>
                </table>
            </body>

            </html><!--/$-->
        """

        # Send emails to confirmed list
        for email in confirmed_emails:
            if send_email(args.email, args.password, email,
                          confirmed_subject, confirmed_body):
                write_log("INFO", f"Sent confirmation email to {email}")
            else:
                write_log(
                    "WARNING", f"Failed to send confirmation email to {email}"
                )

        # Send emails to accepted list
        for email in accepted_emails:
            if send_email(args.email, args.password, email,
                          accepted_subject, accepted_body):
                write_log("INFO", f"Sent acceptance email to {email}")
            else:
                write_log(
                    "WARNING", f"Failed to send acceptance email to {email}"
                )

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
