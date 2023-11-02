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
    err_last = None
    for provider in providers:
        try:
            return provider.last(symbol)
        except Exception as err:
            err_last = err
    raise err_last

def main():
    log.info("Started...")

    # Test
    try:
        print( last('HA') )
    except Exception as err:
        print( err )
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 