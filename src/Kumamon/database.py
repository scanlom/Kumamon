'''
Created on Aug 3, 2013

@author: scanlom
'''

from urllib.request import urlopen
import psycopg2     # Postgresql access
import psycopg2.extras  # Postgresql access
from pandas.io.data import DataReader
from datetime import datetime
from log import log
import config

ADJUSTED_CLOSE = "Adj Close"

def last(symbol):
    url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbol, 'l1')
    str = urlopen(url).read()
    str = str.decode()
    return float(str.strip().strip('"'))

def get_scalar_field(sql, cur, field):
    cur.execute(sql)
    rows = cur.fetchall()
    ret = 0.0 
    if len(rows) > 0:
        ret = rows[0][field]
    
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
        self.cur.execute("select * from portfolio where pricing_type=1")
        rows = self.cur.fetchall()   
    
        for row in rows:
            price = round(last(row['symbol']),2)
            value = round(price * row['quantity'], 2)
            self.cur.execute("update portfolio set price=" + str(price) + ", value=" + str(value) + "where symbol = '" + row['symbol'] + "'")
            
        self.conn.commit()

    def update_stocks_price(self):
        self.cur.execute("select * from stocks")
        rows = self.cur.fetchall()   
    
        for row in rows:
            price = round(last(row['symbol']),2)
            if price > 0:
                self.cur.execute("update stocks set price=" + str(price) + "where symbol = '" + row['symbol'] + "'")
            
        self.conn.commit()
        
    def update_stocks_historicals(self, log):
        self.cur.execute("select * from stocks")
        rows = self.cur.fetchall()   
    
        for row in rows:
            symbol = row['symbol']
            data_symbol = symbol
            if symbol == "BRKB":
                data_symbol = "BRK-B"
            source = "yahoo"
            if symbol.endswith( ".T" ) or symbol == "VDMIX" or symbol== "SAN.PA":
                source = "google"
                continue
            log.info( "Downloading %s..." % ( data_symbol ) )
            data = DataReader( data_symbol,  source, datetime(2000,1,1)) # Get everything back to 2000
            adjusted_close = data[ ADJUSTED_CLOSE ]
            count = len( adjusted_close )
            today = 0
            if count > 0:
                today = adjusted_close[ count - 1 ]
                
            # Day Change
            change = 0
            if count > 1:
                change = round_pct( today / adjusted_close[ count - 2 ] - 1 )
            self.cur.execute("update stocks set day_change=" + str(change) + "where symbol = '" + symbol + "'")

            # Week Change
            change = 0
            if count > 5:
                change = round_pct( today / adjusted_close[ count - 6 ] - 1 )
            self.cur.execute("update stocks set week_change=" + str(change) + "where symbol = '" + symbol + "'")

            # Month Change
            change = 0
            if count > 22:
                change = round_pct( today / adjusted_close[ count - 23 ] - 1 )
            self.cur.execute("update stocks set month_change=" + str(change) + "where symbol = '" + symbol + "'")

            # Three Month Change
            change = 0
            if count > 66:
                change = round_pct( today / adjusted_close[ count - 67 ] - 1 )
            self.cur.execute("update stocks set three_month_change=" + str(change) + "where symbol = '" + symbol + "'")

            # Year Change
            change = 0
            if count > 252:
                change = round_pct( today / adjusted_close[ count - 253 ] - 1 )
            self.cur.execute("update stocks set year_change=" + str(change) + "where symbol = '" + symbol + "'")

            # Five Year Change
            change = 0
            if count > 1260:
                change = round_pct( ( today / adjusted_close[ count - 1261 ] ) ** ( .2 ) - 1 )
            self.cur.execute("update stocks set five_year_change=" + str(change) + "where symbol = '" + symbol + "'")

            # Ten Year Change
            change = 0
            if count > 2520:
                change = round_pct( ( today / adjusted_close[ count - 2521 ] ) ** ( .1 ) - 1 )
            self.cur.execute("update stocks set ten_year_change=" + str(change) + "where symbol = '" + symbol + "'")
            
        self.conn.commit()
