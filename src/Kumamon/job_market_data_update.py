'''
Created on Aug 7, 2013

@author: scanlom
'''
from api_analytics import last
from api_constants import CONST
from api_log import log
from api_blue_lion import ref_data_positions, ref_data_focus, ref_data, market_data_by_symbol, post_market_data, put_market_data

def populate_market_data(i):
    try:
        l = last( i['symbolAlphaVantage'] )
    except Exception as err:
        # If we can't retrieve market data for one symbol, just continue on to the others. We'll catch that in the tech health checks, as market data update time will be stale
        log.warning( "Unable to retrieve last for %s" % (i['symbol']) )
        return
    md = market_data_by_symbol( i['symbol'] )
    if md == None:
        log.info("POST market_data: %s, %f" % (i['symbol'], l))
        post_market_data(i['id'],l)
    else:
        log.info("PUT market_data: %s, %f" % (i['symbol'], l))
        put_market_data(md['id'],i['id'],l)

def main():
    log.info("Started loading market data...")
    instruments_positions = ref_data_positions()
    instruments_focus = ref_data_focus()
    instruments = ref_data()

    # Remove duplicates
    remove_symbols = [i['symbol'] for i in instruments_positions]
    instruments_focus = [i for i in instruments_focus if i['symbol'] not in remove_symbols]
    remove_symbols += [i['symbol'] for i in instruments_focus]
    instruments = [i for i in instruments if i['symbol'] not in remove_symbols]

    # For Testing
    # instruments_positions = [i for i in instruments_positions if i['symbol'] == 'OAYLX']
    # instruments_focus = [i for i in instruments_focus if i['symbol'] == 'OAYLX']
    # instruments = [i for i in instruments if i['symbol'] == 'OAYLX']

    log.info("Loading positions names...")
    curr_call = 0
    for i in instruments_positions:
        curr_call += 2 # Historical run will also be loading positions names
        populate_market_data(i)

    log.info("Loading focus names...")
    curr_call = 0
    for i in instruments_focus:
        curr_call += 2 # Historical run will also be loading focus names
        populate_market_data(i)

    log.info("Loading blurry names...")
    for i in instruments:
        curr_call += 1
        populate_market_data(i)
        if curr_call >=  CONST.MAX_MARKET_DATA_CALLS:
            break

    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")