'''
Created on Mar 07, 2023
@author: scanlom
'''

from json import loads
from time import sleep
from urllib.request import urlopen
from lib_log import log

class market_data_alphavantage:
    
    CONST_THROTTLE_SECONDS  = 16
    CONST_RETRIES           = 1
    CONST_RETRY_SECONDS     = 61

    def __init__(self):
        pass

    def last(self, symbol):
        # Second try is AlphaVantage
        sleep(self.CONST_THROTTLE_SECONDS) # Sleep to avoid throttling errors
        url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=%s&apikey=2YG6SAN57NRYNPJ8' % (symbol)
        retry = 1
        while retry <= self.CONST_RETRIES:
            log.info( "AlphaVantage - Downloading quote for %s" % (symbol) )
            try:
                raw_bytes = urlopen(url).read()
                data = loads(raw_bytes.decode())
                last = round( float(data['Global Quote']['05. price']), 2 )
                return last
            except Exception as err:
                if retry >= self.CONST_RETRIES:
                    log.warning( "AlphaVantage - Unable to retrieve last for %s" % (symbol) )
                    log.info( data )
                    raise err
                else:
                    log.warning( "AlphaVantage - Unable to retrieve last for %s, retry %d" % (symbol, retry) )
                    retry += 1
                    sleep(self.CONST_RETRY_SECONDS) # For some reason AlphaVantage is not returning, sleep to try and allow them to recover         

def main():
    log.info("Started...")

    # Test
    foo  = market_data_alphavantage()
    print( foo.last('HA') )
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 