'''
Created on Oct 27, 2018

@author: scanlom
'''

from datetime import date
from api_analytics import get_market_data_symbol
from api_analytics import historicals
from api_database import database2
from api_log import log
           
def main():
    log.info("Started...")
    symbol = "1373.HK"
    from_date = date(2013,1,1)
    db = database2()
    rows = db.get_fundamentals(symbol, from_date)
    h = historicals( get_market_data_symbol( symbol ) )
    for row in rows:
        close = h.close(row.date)
        high = h.year_high(row.date)
        low = h.year_low(row.date)
        pe = round( close / row.eps )
        pe_high = round( high / row.eps )
        pe_low = round( low / row.eps )
        mkt_cap = round( row.shrs_out * close )
        print( "%s %s PE: %d %f / %f PE High: %d %f / %f PE Low: %d %f / %f Mkt Cap: %d %f * %f" % (row.date, row.symbol, pe, close, row.eps, pe_high, high, row.eps, pe_low, low, row.eps, mkt_cap, row.shrs_out, close))
        action = input( "Please input y to commit, n to skip, a to abort:" )
        if action == "y":
            row.pe = pe
            row.pe_high = pe_high
            row.pe_low = pe_low
            row.mkt_cap = mkt_cap
            db.commit()
        elif action == "n":
            continue
        elif action == "a":
            break
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 