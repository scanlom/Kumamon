'''
Created on Nov 13, 2017

@author: scanlom
'''

from collections import OrderedDict
from datetime import date
from datetime import datetime
from decimal import Decimal
from json import loads
from time import sleep
from urllib.request import urlopen
from api_log import log

CONST_THROTTLE_SECONDS  = 16
CONST_RETRIES           = 5
CONST_RETRY_SECONDS     = 61

def get_market_data_symbol(symbol):
    if symbol == "BRKB":
        return "BRK-B"
    return symbol

# AlphaVantage may return some garbage data, we do our best to avoid that here
def sanity_check_historical_data(key, value):
    adj_close = Decimal( value['5. adjusted close'] )
    
    if adj_close <= 0:
        return False
    
    return True

def last(symbol):
    retry = 1
    sleep(CONST_THROTTLE_SECONDS) # Sleep to avoid AlphaVantage throttling error
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&apikey=2YG6SAN57NRYNPJ8' % (symbol)
   
    while retry <= CONST_RETRIES:
        try:
            raw_bytes = urlopen(url).read()
            data = loads(raw_bytes.decode())
            last = Decimal( data['Time Series (Daily)'][ data['Meta Data']['3. Last Refreshed'][0:10] ]['5. adjusted close'] )
            return last
        except Exception as err:
            if retry >= CONST_RETRIES:
                log.error( "Unable to retrieve last for %s" % (symbol) )
                log.info( data )
                raise err
            else:
                log.warning( "Unable to retrieve last for %s, retry %d" % (symbol, retry) )
                retry += 1
                sleep(CONST_RETRY_SECONDS) # For some reason AlphaVantage is not returning, sleep to try and allow them to recover              

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

        retry = 1
        while retry <= CONST_RETRIES:
            try:
                sleep(CONST_THROTTLE_SECONDS) # Sleep to avoid AlphaVantage throttling error
                url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&outputsize=full&apikey=2YG6SAN57NRYNPJ8' % (symbol)
                raw_bytes = urlopen(url).read()
                data_full = loads(raw_bytes.decode(), object_pairs_hook=OrderedDict)
        
                sleep(CONST_THROTTLE_SECONDS) # Sleep to avoid AlphaVantage throttling error
                url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&apikey=2YG6SAN57NRYNPJ8' % (symbol)
                raw_bytes = urlopen(url).read()
                data_compact = loads(raw_bytes.decode(), object_pairs_hook=OrderedDict)
        
                # For outputsize=full, TiME_SERIES_DAILY_ADJUSTED is one week delayed.  So we have to get the compact information,
                # store it, and then add the rest from full
                
                self.data_adj_close = OrderedDict()
                self.data_close = OrderedDict() 
                self.data_high = OrderedDict() 
                self.data_low = OrderedDict() 
                for key, value in data_compact['Time Series (Daily)'].items():
                    if sanity_check_historical_data(key, value):
                        self.data_adj_close[key] = Decimal( value['5. adjusted close'] )
                        self.data_close[key] = Decimal( value['4. close'] )
                        self.data_high[key] = Decimal( value['2. high'] )
                        self.data_low[key] = Decimal( value['3. low'] )
        
                for key, value in data_full['Time Series (Daily)'].items():
                    if sanity_check_historical_data(key, value):
                        if not (key in self.data_adj_close):
                            self.data_adj_close[key] = Decimal( value['5. adjusted close'] )
                        if not (key in self.data_close):
                            self.data_close[key] = Decimal( value['4. close'] )
                        if not (key in self.data_high):
                            self.data_high[key] = Decimal( value['2. high'] )
                        if not (key in self.data_low):
                            self.data_low[key] = Decimal( value['3. low'] )
                        
                self.data_adj_close = list( self.data_adj_close.items() )
                self.data_close = list( self.data_close.items() )
                self.data_high = list( self.data_high.items() )
                self.data_low = list( self.data_low.items() )
                break
            except Exception as err:
                if retry >= CONST_RETRIES:
                    log.error( "Unable to retrieve historicals for %s" % (self.symbol) )
                    log.info( data_compact )
                    raise err
                else:
                    log.warning( "Unable to retrieve historicals for %s, retry %d" % (self.symbol, retry) )
                    retry += 1
                    sleep(CONST_RETRY_SECONDS) # For some reason AlphaVantage is not returning, sleep to try and allow them to recover              

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
            log.warning( "Off the end of the historicals list for %s, %d / %d" % (self.symbol, days, len(self.data_adj_close) ) )
            days = len(self.data_adj_close) - 1
        
        # How many years are we compounding?
        years = 1
        if days > self.CONST_BUSINESS_DAYS_YEAR:
            years = days / self.CONST_BUSINESS_DAYS_YEAR
            
        return ( self.data_adj_close[ days ][ 0 ], ( self.data_adj_close[ 0 ][ 1 ] / self.data_adj_close[ days ][ 1 ] ) ** Decimal( 1 / years ) - 1 )    
        
    def close(self, date):
        # Return the close on this date or the first previous day
        for close in self.data_close:
            close_date = datetime.strptime(close[0], '%Y-%m-%d').date()
            if close_date <= date:
                return close[1]
            
        raise LookupError()
    
    def year_high(self, end_date):
        # Return the highest close for the year ending on date
        ret = -1
        start_date = date(end_date.year - 1, end_date.month, end_date.day)
        for high in self.data_high:
            high_date = datetime.strptime(high[0], '%Y-%m-%d').date()
            if high_date <= end_date and high_date > start_date:
                if high[1] > ret:
                    ret = high[1]
            if high_date <= start_date:
                return ret
            
        raise LookupError()

    def year_low(self, end_date):
        # Return the highest close for the year ending on date
        ret = -1
        start_date = date(end_date.year - 1, end_date.month, end_date.day)
        for low in self.data_low:
            low_date = datetime.strptime(low[0], '%Y-%m-%d').date()
            if low_date <= end_date and low_date > start_date:
                if low[1] < ret or ret == -1:
                    ret = low[1]
            if low_date <= start_date:
                return ret
            
        raise LookupError()
              
def main():
    log.info("Started...")
    
    # Test
    print( last('WFC') )
    
    foo = historicals('3030.T')
    print( foo.change_ten_years()[0] )
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 