'''
Created on Dec 8, 2019

@author: scanlom
'''

from api_database import database2
from api_log import log
from api_mail import send_mail_html_self
from api_reporting import report

def main():
    log.info("Started...")
    db = database2()
    rpt = report()
  
    subject = 'Blue Lion - Search'
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")