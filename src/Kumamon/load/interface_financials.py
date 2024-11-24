'''
Created on Nov 19, 2024
@author: scanlom

Interface files layer an abstraction between third party external data providers and our application code
'''

from lib_log import log
from provider_yahooquery import financials_yahooquery

providers = [ financials_yahooquery() ]

def financials_by_ticker(symbol):
    err_last = None
    for provider in providers:
        try:
            return provider.financials_by_ticker(symbol)
        except Exception as err:
            err_last = err
    raise err_last

def main():
    log.info("Started...")

    # Test
    print( financials_by_ticker('1373.HK') )
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 