'''
Created on Mar 07, 2023
@author: scanlom

Interface files layer an abstraction between third party external data providers and our application code
'''

from lib_log import log
from provider_alphavantage import market_data_alphavantage
from provider_yahooquery import market_data_yahooquery

providers = [ market_data_yahooquery(), market_data_alphavantage() ]

def last(symbol):
    for provider in providers:
        try:
            return provider.last(symbol)
        except Exception as err:
            pass
    raise err

def main():
    log.info("Started...")

    # Test
    print( last('HA') )
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 