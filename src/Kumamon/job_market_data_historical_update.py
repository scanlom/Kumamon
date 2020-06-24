'''
Created on Aug 7, 2013

@author: scanlom
'''

from api_analytics import historicals
from api_log import log
from api_blue_lion import ref_data_focus, mdh_by_ref_data_id_date, post_market_data_historical, put_market_data_historical

def main():
    log.info("Started loading market data...")
    instruments = ref_data_focus()
    for i in instruments:
        try:
            h = historicals( i['symbolAlphaVantage'] )
        except Exception as err:
            # Log exceptions as warnings, there often won't be historical data for international names
            log.warning( "Could not get data for %s" % ( i['symbol'] ) )
            continue   
        log.info("Populating for %s" % (i['symbol']))
        post = 0
        put = 0
        for close, adj_close in zip(h.data_close, h.data_adj_close):
            if close[0] != adj_close[0]:
                raise RuntimeError('Date mismatch: close: %s, adj_close: %s' % (close[0], adj_close[0]))
            mdh = mdh_by_ref_data_id_date(i['id'],close[0])
            if mdh == None:
                post_market_data_historical( close[0], i['id'], close[1], adj_close[1] )
                post += 1
            else:   
                put_market_data_historical( mdh['id'], close[0], i['id'], close[1], adj_close[1] )
                put += 1
        log.info("Posted %d records, Put %d records" % (post, put))
    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")