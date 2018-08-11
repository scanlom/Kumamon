'''
Created on Nov 13, 2017

@author: scanlom
'''

import json
import time
from decimal import Decimal
from log import log
from urllib.request import urlopen
from collections import OrderedDict

CONST_THROTTLE_SECONDS             = 16

def last(symbol):
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&apikey=2YG6SAN57NRYNPJ8' % (symbol)
    raw_bytes = urlopen(url).read()
    data = json.loads(raw_bytes.decode())
    
    try:
        last = Decimal( data['Time Series (Daily)'][ data['Meta Data']['3. Last Refreshed'][0:10] ]['5. adjusted close'] )
        time.sleep(CONST_THROTTLE_SECONDS) # Sleep to avoid AlphaVantage throttling error
        return last
    except Exception as err:
        log.error( "Unable to retrieve last for %s" % (symbol) )
        log.info( data )
        raise err

class historicals:
    CONST_BUSINESS_DAYS_ONE             = 1
    CONST_BUSINESS_DAYS_WEEK            = 5
    CONST_BUSINESS_DAYS_MONTH           = 22
    CONST_BUSINESS_DAYS_THREE_MONTHS    = 66
    CONST_BUSINESS_DAYS_YEAR            = 252
    CONST_BUSINESS_DAYS_FIVE_YEARS      = 1260
    CONST_BUSINESS_DAYS_TEN_YEARS       = 2520
    
    def __init__(self, symbol):
        self.symbol = symbol
        
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&outputsize=full&apikey=2YG6SAN57NRYNPJ8' % (symbol)
        bytes = urlopen(url).read()
        data_full = json.loads(bytes.decode(), object_pairs_hook=OrderedDict)

        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&apikey=2YG6SAN57NRYNPJ8' % (symbol)
        bytes = urlopen(url).read()
        data_compact = json.loads(bytes.decode(), object_pairs_hook=OrderedDict)

        # For outputsize=full, TiME_SERIES_DAILY_ADJUSTED is one week delayed.  So we have to get the compact information,
        # store it, and then add the rest from full
        
        self.data_adj_close = OrderedDict() 
        for key, value in data_compact['Time Series (Daily)'].items():
            self.data_adj_close[key] = Decimal( value['5. adjusted close'] )

        for key, value in data_full['Time Series (Daily)'].items():
            if not (key in self.data_adj_close):
                self.data_adj_close[key] = Decimal( value['5. adjusted close'] )
                
        self.data_adj_close = list( self.data_adj_close.items() )

    def change_one_day(self):
        return self.change(self.CONST_BUSINESS_DAYS_ONE )

    def change_one_week(self):
        return self.change(self.CONST_BUSINESS_DAYS_WEEK )
    
    def change_one_month(self):
        return self.change(self.CONST_BUSINESS_DAYS_MONTH )
    
    def change_three_months(self):
        return self.change(self.CONST_BUSINESS_DAYS_THREE_MONTHS )

    def change_one_year(self):
        return self.change(self.CONST_BUSINESS_DAYS_YEAR )
    
    def change_five_years(self):
        return self.change(self.CONST_BUSINESS_DAYS_FIVE_YEARS )
    
    def change_ten_years(self):
        return self.change(self.CONST_BUSINESS_DAYS_TEN_YEARS )

    def change(self, days):
        # Make sure we're not off the end of the list - if we are, use the last one
        if days >= len(self.data_adj_close):
            days = len(self.data_adj_close) - 1
        
        # How many years are we compounding?
        years = 1
        if days > self.CONST_BUSINESS_DAYS_YEAR:
            years = days / self.CONST_BUSINESS_DAYS_YEAR
            
        return ( self.data_adj_close[ days ][ 0 ], ( self.data_adj_close[ 0 ][ 1 ] / self.data_adj_close[ days ][ 1 ] ) ** Decimal( 1 / years ) - 1 )    
          
def main():
    log.info("Started...")
    
    # Test
    print( last('WFC') )
    
    foo = historicals('MSFT')
    print( foo.change_one_day()[0] )
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 