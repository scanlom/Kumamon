'''
Created on Aug 7, 2013

@author: scanlom
'''
from api_analytics import last
from api_log import log
from api_blue_lion import ref_data_focus, market_data_by_symbol, post_market_data, put_market_data

def main():
    log.info("Started loading market data...")
    instruments = ref_data_focus()
    for i in instruments:
        try:
            l = last( i['symbolAlphaVantage'] )
        except Exception as err:
            # If we can't retrieve market data for one symbol, just continue on to the others. We'll catch that in the tech health checks, as market data update time will be stale
            log.warning( "Unable to retrieve last for %s" % (i['symbol']) )
            continue
        md = market_data_by_symbol( i['symbol'] )
        if md == None:
            log.info("POST market_data: %s, %f" % (i['symbol'], l))
            post_market_data(i['id'],l)
        else:
            log.info("PUT market_data: %s, %f" % (i['symbol'], l))
            put_market_data(md['id'],i['id'],l)

    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")