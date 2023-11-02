'''
Created on Mar 07, 2023
@author: scanlom

yahooquery scrapes the yahoo finance web site so there are often problems. When these arise first check
https://github.com/dpguthrie/yahooquery for a new version, or if any issues reference the problem
'''

from yahooquery import Ticker
from lib_log import log

class market_data_yahooquery:
    
    def __init__(self):
        pass

    def last(self, symbol):
        raise Exception("Test")
        try:
            log.info( "Yahoo Finance - Downloading quote for %s" % (symbol) )
            ticker = Ticker(symbol)
            return round(ticker.price[symbol]['regularMarketPrice'], 2)
        except Exception as err:
            log.warning( "Yahoo Finance - Unable to retrieve last for %s" % (symbol) )
            raise err
        
class ref_data_yahooquery:
    
    def __init__(self):
        pass

    def ref_data_by_ticker(self, symbol):
        try:
            log.info( "Yahoo Finance - Downloading quote for %s" % (symbol) )
            ticker = Ticker(symbol)
            summary = ticker.summary_profile
            quote = ticker.price
            return {
                'description': quote[symbol]['longName'],
                'sector': summary[symbol]['sector'],
                'industry': summary[symbol]['industry'],
            }
        except Exception as err:
            log.warning( "Yahoo Finance - Unable to retrieve product for %s" % (symbol) )
            raise err

def main():
    log.info("Started...")

    # Test
    foo  = market_data_yahooquery()
    print( foo.last('HA') )
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 