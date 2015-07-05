'''
Created on Aug 3, 2013

@author: scanlom
'''

from urllib.request import urlopen
import psycopg2     # Postgresql access
import psycopg2.extras  # Postgresql access
from pandas.io.data import DataReader
from datetime import datetime
from datetime import date
from log import log
from decimal import *
import config

ADJUSTED_CLOSE = "Adj Close"

def last(symbol):
    url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbol, 'l1')
    str = urlopen(url).read()
    str = str.decode()
    return Decimal(str.strip().strip('"'))

def get_scalar_field(sql, cur, field):
    cur.execute(sql)
    rows = cur.fetchall()
    ret = Decimal(0.0) 
    if len(rows) > 0:
        ret = Decimal(rows[0][field])
    
    return ret 

def get_scalar(sql, cur):
    return get_scalar_field(sql, cur, 'value')

def round_ccy(value):
    return round(value, 2)

def round_pct(value):
    return round(value, 4)

class finances(object):

    def __init__(self):
        self.conn = psycopg2.connect( config.config_database_connect )
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
    def __del__(self):
        self.cur.close()
        self.conn.close()

    def recon_budget(self):
        return round(self.get_budget_pos() - self.get_budget_neg(), 2)
   
    def get_budget_pos(self):
        self.cur.execute("select * from balances where recon_budget_pos=true")
        rows = self.cur.fetchall()   
    
        total = 0
        for row in rows:
            total += row['value']
        return total

    def get_budget_neg(self):
        self.cur.execute("select * from balances where recon_budget_neg=true")
        rows = self.cur.fetchall()   
    
        total = 0
        for row in rows:
            total += row['value']
        return total
       
    def update_portfolio_price_value(self):
        self.cur.execute("select * from constituents where pricing_type=1")
        rows = self.cur.fetchall()   
    
        for row in rows:
            symbol = row['symbol']
            log.info( "Downloading %s..." % ( symbol ) )
            price = round(last( symbol ),2)
            value = round(price * row['quantity'], 2)
            log.info( "Updating %s..." % ( symbol ) )
            self.cur.execute("update constituents set price=" + str(price) + ", value=" + str(value) + " where symbol = '" + row['symbol'] + "'")
            
        log.info( "Committing transaction..." )
        self.conn.commit()
        log.info( "Done" )

    def update_stocks_price(self):
        self.cur.execute("select * from stocks")
        rows = self.cur.fetchall()   
    
        for row in rows:
            symbol = row['symbol']
            log.info( "Downloading %s..." % ( symbol ) )
            price = 0
            try:
                price = round(last( symbol ),2)
            except Exception as err:
                log.error( "Could not get price for %s" % ( symbol ) )
                log.exception(err)
                continue    
            if price > 0:
                sql = "update stocks set price=" + str(price) + " where symbol = '" + symbol + "'"
                log.info( "SQL: %s" % ( sql ) )
                self.cur.execute( sql )
        log.info( "Committing transaction..." )
        self.conn.commit()
        log.info( "Done" )
            
    def update_stock_historical_change(self, symbol, index, field, field_date, close, 
                                       historical_closes, historical_close_dates, years):
        change = 0
        change_date = date.today()
        count = len( historical_closes )
        if count > index:
            change = round_pct( ( close / historical_closes[ count - ( index + 1 ) ] ) ** ( 1 / years ) - 1 )
            change_date = historical_close_dates[ count - ( index + 1 ) ]
        self.cur.execute( "update stocks set %s = %s, %s = '%s'  where symbol = '%s'" % 
                          ( field, str( change ), field_date, change_date.strftime( "%m-%d-%y" ), symbol  ) )

    def update_stocks_historicals(self, log):
        self.cur.execute("select * from stocks")
        rows = self.cur.fetchall()   
    
        for row in rows:
            symbol = row['symbol']
            data_symbol = symbol
            if symbol == "BRKB":
                data_symbol = "BRK-B"
            source = "yahoo"
            log.info( "Downloading %s..." % ( data_symbol ) )
            try:
                data = DataReader( data_symbol,  source, datetime(2003,1,1)) # Get everything back to 2003
            except Exception as err:
                log.error( "Could not get data for %s" % ( data_symbol ) )
                log.exception(err)
                continue
            historical_closes = data[ ADJUSTED_CLOSE ]
            historical_close_dates = data.index
            count = len( historical_closes )
            close = 0
            if count > 0:
                close = historical_closes[ count - 1 ]
            
            self.update_stock_historical_change( symbol, 1, "day_change", "day_change_date", close, historical_closes, historical_close_dates, 1 )
            self.update_stock_historical_change( symbol, 5, "week_change", "week_change_date", close, historical_closes, historical_close_dates, 1 )    
            self.update_stock_historical_change( symbol, 22, "month_change", "month_change_date", close, historical_closes, historical_close_dates, 1 )    
            self.update_stock_historical_change( symbol, 66, "three_month_change", "three_month_change_date", close, historical_closes, historical_close_dates, 1 )    
            self.update_stock_historical_change( symbol, 252, "year_change", "year_change_date", close, historical_closes, historical_close_dates, 1 )    
            self.update_stock_historical_change( symbol, 1260, "five_year_change", "five_year_change_date", close, historical_closes, historical_close_dates, 5 )    
            self.update_stock_historical_change( symbol, 2520, "ten_year_change", "ten_year_change_date", close, historical_closes, historical_close_dates, 10 )    
            
        self.conn.commit()
