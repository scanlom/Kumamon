'''
Created on Jan 1, 2014

@author: scanlom
'''

from psycopg2 import connect
from psycopg2.extras import DictCursor
from api_config import config_database_connect
from api_log import log

def main():
    log.info("Started job_yearly.py...")
    
    conn = connect( config_database_connect )
    cur = conn.cursor(cursor_factory=DictCursor)
    
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
