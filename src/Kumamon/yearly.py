'''
Created on Jan 1, 2014

@author: scanlom
'''

import mail, database, config
from log import log

def main():
    log.info("Started yearly.py...")
    db = database.finances()
    
    # Zero out Paid, Tax and Savings
    db.set_paid(0)
    db.set_tax(0)
    db.set_savings(0)
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
        mail.send_mail_html_self("FAILURE:  portfolio.py", str( err ) ) 