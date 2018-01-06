'''
Created on Nov 13, 2017

@author: scanlom
'''

import json
from decimal import *
from log import log
from urllib.request import urlopen

def last(symbol):
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&apikey=2YG6SAN57NRYNPJ8' % (symbol)
    bytes = urlopen(url).read()
    data = json.loads(bytes.decode())
    return Decimal( data['Time Series (Daily)'][ data['Meta Data']['3. Last Refreshed'][0:10] ]['5. adjusted close'] )

def main():
    log.info("Started...")
    
    # Test
    print( last('BRK-B') )
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 