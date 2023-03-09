'''
Created on Mar 07, 2023
@author: scanlom
'''

from yahooquery import Ticker
from api_log import log

class market_data_yahooquery:
    
    def __init__(self):
        pass

    def last(self, symbol):
        try:
            log.info( "Yahoo Finance - Downloading quote for %s" % (symbol) )
            ticker = Ticker(symbol)
            return round(ticker.price[symbol]['regularMarketPrice'], 2)
        except Exception as err:
            log.warning( "Yahoo Finance - Unable to retrieve last for %s" % (symbol) )
            raise err
        
class product_data_yahooquery:
    
    def __init__(self):
        pass

    def product(self, symbol):
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
    foo = product_data_yahooquery()
    print( foo.product('HA') )
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 