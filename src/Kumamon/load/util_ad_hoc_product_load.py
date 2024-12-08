'''
Created on Jan 27, 2022
@author: scanlom
'''

import api_blue_lion as _abl
from interface_ref_data import ref_data_by_ticker
from interface_market_data import last
from lib_log import log

def main():
    log.info("Started...")

    ticker = "VIV.PA"
    newRd = ref_data_by_ticker(ticker)
    oldRd = _abl.ref_data_by_symbol(ticker)
    if (oldRd is not None):
        log.info("Putting ref_data for " + ticker)
        _abl.put_ref_data(oldRd['id'], oldRd['symbol'], oldRd['symbolAlphaVantage'], newRd['description'], newRd['sector'], newRd['industry'], True)
    else:
        log.info("Posting ref_data for " + ticker)
        _abl.post_ref_data(ticker, newRd['description'], newRd['sector'], newRd['industry'])
    newRd = _abl.ref_data_by_symbol(ticker) # Get the new ID

    newLast = last(ticker)
    oldMd = _abl.market_data_by_symbol(ticker)
    if (oldMd is not None):
        log.info("Putting market_data for " + ticker)
        _abl.put_market_data(oldMd['id'], oldMd['refDataId'], newLast)
    else:
        log.info("Posting market_data for " + ticker)
        _abl.post_market_data(newRd['id'], newLast)

    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")