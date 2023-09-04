'''
Created on Mar 07, 2023
@author: scanlom

Interface files layer an abstraction between third party external data providers and our application code
'''

from lib_log import log
from provider_yahooquery import ref_data_yahooquery

providers = [ ref_data_yahooquery() ]

def ref_data_by_ticker(symbol):
    for provider in providers:
        try:
            return provider.ref_data_by_ticker(symbol)
        except Exception as err:
            pass
    raise err

def main():
    log.info("Started...")

    # Test
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 