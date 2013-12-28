'''
Created on Nov 30, 2013

@author: scanlom
'''

import mail, database
from pandas.io.data import DataReader
from datetime import datetime
from log import log

def main():
    log.info("Started...")
    db = database.finances()
    db.update_stocks_historicals( log )
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
        mail.send_mail_html_self("FAILURE:  historicalownload.py", str( err ) ) 
