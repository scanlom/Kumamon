'''
Created on Aug 7, 2013

@author: scanlom
'''

from api_analytics import historicals
from api_log import log
from api_blue_lion import ref_data, post_market_data_historical, delete_market_data_historical

def main():
    log.info("Started loading market data...")
    instruments = ref_data()
    for i in instruments:
        # Do a delete first, to clear out the db (if historicals panics, leaving us with no data, that's ok. we don't want the stale stuff)
        delete_market_data_historical(i['symbol'])
        try:
            h = historicals( i['symbolAlphaVantage'] )
        except Exception as err:
            # Log exceptions as warnings, there often won't be historical data for international names
            log.warning( "Could not get data for %s" % ( i['symbol'] ) )
            continue   
        log.info("Posting for %s" % (i['symbol']))
        for close, adj_close in zip(h.data_close, h.data_adj_close):
            if close[0] != adj_close[0]:
                raise RuntimeError('Date mismatch: close: %s, adj_close: %s' % (close[0], adj_close[0]))
            post_market_data_historical( close[0], i['id'], close[1], adj_close[1] )
        log.info("Posted %d records" % (len(h.data_close)))
    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")