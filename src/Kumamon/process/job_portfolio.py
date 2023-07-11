'''
Created on Jul 20, 2013
@author: scanlom
'''

from psycopg2 import connect
from psycopg2.extras import DictCursor
from lib_config import config_database_connect
from lib_log import log
import api_blue_lion as _abl

def format_ccy_sql(number):
    return str(round(number,2))

def main():
    log.info("Started...")

    conn = connect( config_database_connect )
    cur = conn.cursor(cursor_factory=DictCursor)
    
    # Update balances_history with today's values
    cur.execute("delete from balances_history where date=current_date")
    cur.execute("insert into balances_history (select current_date, type, value from balances)")
    conn.commit()
    
    # Close the db
    cur.close()
    conn.close()
    
    # Run Sanomaru
    status = _abl.run_job_valuation_cut()
    log.info("Valuation Cut Successful, Status %d" % (status))

    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")