'''
Created on Aug 3, 2013

@author: scanlom
'''

from email.mime.text import MIMEText
from smtplib import SMTP
from api_config import config_email_server
from api_config import config_email_port
from api_config import config_email_user
from api_config import config_email_password

def send_mail_msg(to, subject, msg):
    msg['Subject'] = subject
    msg['From'] = config_email_user
    msg['To'] = to

    # Send the message via our own SMTP server.
    s = SMTP(config_email_server, config_email_port)
    s.ehlo()
    s.starttls()
    s.ehlo
    s.login(config_email_user, config_email_password)
    s.send_message(msg)
    s.quit()

def send_mail_html(to, subject, body):
    msg = MIMEText(body, 'html')
    send_mail_msg(to, subject, msg)

def send_mail_html_self(subject, body):
    send_mail_html(config_email_user, subject, body)    