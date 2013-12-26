'''
Created on Aug 7, 2013

@author: scanlom
'''

import mail, database
from log import log

def main():
    log.info("Started...")
    db = database.finances()
    db.update_portfolio_price_value()
    db.update_stocks_price()
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
        mail.send_mail_html_self("FAILURE:  pricedownload.py", str( err ) ) 
        



    