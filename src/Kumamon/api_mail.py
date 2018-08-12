'''
Created on Aug 3, 2013

@author: scanlom
'''

import smtplib, configparser, os
from email.mime.text import MIMEText

def send_mail_msg(to, subject, msg):
    config = configparser.SafeConfigParser()
    config.read(os.path.expanduser('~/.Kumamon'))
    server = config.get('Email','Server')
    port = config.getint('Email','Port')
    from_address = config.get('Email','User')
    password = config.get('Email','Password')
    to_address = config.get('Email',to)

    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address

    # Send the message via our own SMTP server.
    s = smtplib.SMTP(server, port)
    s.ehlo()
    s.starttls()
    s.ehlo
    s.login(from_address, password)
    s.send_message(msg)
    s.quit()

def send_mail_html(to, subject, body):
    msg = MIMEText(body, 'html')
    send_mail_msg(to, subject, msg)

def send_mail_html_self(subject, body):
    send_mail_html('User', subject, body)
    
def send_mail_html_fumi(subject, body):
    send_mail_html('Fumi', subject, body)
    