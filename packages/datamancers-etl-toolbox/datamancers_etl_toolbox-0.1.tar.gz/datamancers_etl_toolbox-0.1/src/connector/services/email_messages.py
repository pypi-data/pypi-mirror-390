import os.path
import base64
import imaplib
import email
from typing import List
import logging

# Configure the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EmailClient:
    def __init__(self, email_user: str, email_pass: str, imap_url: str = 'imap.gmail.com'):
        """
        Initializes the EmailClient with the given email credentials and IMAP URL.
        """
        self.email_user = email_user
        self.email_pass = email_pass
        self.imap_url = imap_url
        self.mail = self.login()

    def login(self):
        """
        Logs into the email server using IMAP and returns the connection object.
        """
        mail = imaplib.IMAP4_SSL(self.imap_url)
        try:
            mail.login(self.email_user, self.email_pass)
            logger.info("Login successful for user: %s", self.email_user)
        except imaplib.IMAP4.error as e:
            logger.error("Login failed for user: %s. Error: %s", self.email_user, e)
            return None
        logger.info("Connected to IMAP server: %s", self.imap_url)
        return mail
    def convert_message_to_dict(self, msg) -> dict:
        """
        Converts an email message to a dictionary containing relevant details.
        """
        payload=msg.get_payload(decode=True) if not msg.is_multipart() else msg.get_payload()
        
        if isinstance(payload, list):
            payload_list=''
            for i in payload:
                if i.get_content_type() == 'text/plain':
                    payload_list+=i.get_payload(decode=True).decode()
            payload=payload_list
        else:
            payload=payload.decode()
        email_dict = {
            'from': msg['from'],
            'to': msg['to'],
            'subject': msg['subject'],
            'date': msg['date'],
            'content': payload
        }
        return email_dict
    def list_emails(self, output_format: str = 'dict',condition: str = None) -> List[dict]:
        """
        Lists all unread emails and returns them as a list of email objects.
        """
        self.mail.select('inbox')
        logger.info("Searching for emails with condition: %s", condition)
        result, data = self.mail.search(None, condition)
        email_ids = data[0].split()
        logger.info("Number of emails listed: %d", len(email_ids))
        if len(email_ids) == 0:
            logger.info("No emails found. Ending function.")
            return []
        email_objects = []
        for e_id in email_ids:
            result, msg_data = self.mail.fetch(e_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            if output_format == 'dict':
                email_objects.append(self.convert_message_to_dict(msg))
            else:
                email_objects.append(msg)
        return email_objects

# Example usage:
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Email client to fetch unread emails.')
    email_user = os.environ.get('EMAIL_USER')
    if email_user is None:
        logger.error("Email user not found in arguments or environment variables.")
    
    email_pass = os.environ.get('EMAIL_PASS')
    if email_pass is None:
        logger.error("Email password not found in arguments or environment variables.")
    
    parser.add_argument('email_user', type=str, help='Email user', default=email_user)
    parser.add_argument('email_pass', type=str, help='Email password', default=email_pass)
    parser.add_argument('--imap_url', type=str, default=os.environ.get('IMAP_URL', 'imap.gmail.com'), help='IMAP server URL')
    parser.add_argument('--condition', type=str, help='Search condition for emails',default='UNSEEN')
    parser.add_argument('--path', type=str, help='Path to save the output JSON file', default='mails.json')
    args = parser.parse_args()

    email_user = args.email_user
    email_pass = args.email_pass
    imap_url = args.imap_url
    condition = args.condition
    output_path = args.path

    
    client = EmailClient(email_user, email_pass, imap_url)
    import json
    unread_emails = client.list_emails(condition=condition)
    with open(output_path, 'w') as json_file:
        nld_json="\n".join([json.dumps(i) for i in unread_emails])
        json_file.write(nld_json)
    