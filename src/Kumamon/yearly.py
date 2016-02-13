'''
Created on Jan 1, 2014

@author: scanlom
'''

import mail, database, config
from log import log
import psycopg2     # Postgresql access
import psycopg2.extras  # Postgresql access

def main():
    log.info("Started yearly.py...")
    
    conn = psycopg2.connect( config.config_database_connect )
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("update balances set value=0 where type=15")    # Paid
    cur.execute("update balances set value=0 where type=16")    # Tax
    cur.execute("update balances set value=0 where type=17")    # Savings
    conn.commit()
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
        mail.send_mail_html_self("FAILURE:  portfolio.py", str( err ) ) 