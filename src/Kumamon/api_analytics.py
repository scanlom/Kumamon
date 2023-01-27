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
import api_fundamentals as _af
from api_log import log

CONST_THROTTLE_SECONDS  = 16
CONST_RETRIES           = 1
CONST_RETRY_SECONDS     = 61

def last(symbol):
    # First try is yahoo finance (no throttling necessary)
    try:
        log.info( "Yahoo Finance - Downloading quote for %s" % (symbol) )
        quote = _af.get_quote(symbol)
        return round(quote['QuoteSummaryStore']['price']['regularMarketPrice']['raw'], 2)
    except Exception as err:
        log.warning( "Yahoo Finance - Unable to retrieve last for %s" % (symbol) )
    
    # Second try is AlphaVantage
    sleep(CONST_THROTTLE_SECONDS) # Sleep to avoid throttling errors
    url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=%s&apikey=2YG6SAN57NRYNPJ8' % (symbol)
    retry = 1
    while retry <= CONST_RETRIES:
        log.info( "AlphaVantage - Downloading quote for %s" % (symbol) )
        try:
            raw_bytes = urlopen(url).read()
            data = loads(raw_bytes.decode())
            last = Decimal( data['Global Quote']['05. price'] )
            return last
        except Exception as err:
            if retry >= CONST_RETRIES:
                log.warning( "AlphaVantage - Unable to retrieve last for %s" % (symbol) )
                log.info( data )
                raise err
            else:
                log.warning( "AlphaVantage - Unable to retrieve last for %s, retry %d" % (symbol, retry) )
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

        try:
            prices = _af.get_historicals(symbol)['HistoricalPriceStore']['prices']
            self.data_adj_close = []
            self.data_close = []
            self.data_high = []
            self.data_low = []
            for price in prices:
                if 'type' in price:
                    continue # Skip corporate actions
                date_str = datetime.utcfromtimestamp(price['date']).strftime('%Y-%m-%d')
                self.data_adj_close.append([ date_str, Decimal(round(price['adjclose'],2)) ])
                self.data_close.append([ date_str, Decimal(round(price['close'],2)) ])
                self.data_high.append([ date_str, Decimal(round(price['high'],2)) ])
                self.data_low.append([ date_str, Decimal(round(price['low'],2)) ])
    
        except Exception as err:
            log.warning( "Unable to retrieve historicals for %s" % (self.symbol) )
            raise err

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
    print( last('HA') )
    
    # foo = historicals('BAS.F')
    # print( foo.change_ten_years()[0] )
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 