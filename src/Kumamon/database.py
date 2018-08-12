'''
Created on Aug 3, 2013

@author: scanlom
'''

from urllib.request import urlopen
import psycopg2     # Postgresql access
import psycopg2.extras  # Postgresql access
from datetime import datetime
from datetime import date
from log import log
from decimal import *
from api_analytics import *
import config

ADJUSTED_CLOSE = "Adj Close"

def get_scalar_field(sql, cur, field):
    log.info( "get_scalar_field: " + sql )
    cur.execute(sql)
    rows = cur.fetchall()
    ret = Decimal(0.0) 
    if len(rows) > 0 and rows[0][field] is not None: 
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

    def get_spending_sum(self, type_str):
        return get_scalar_field("select sum(amount) as amount from spending where type in (" + \
                                type_str + ") and date >= '" + date.today().strftime( "01-01-%y" ) + "'", \
                                self.cur, "amount")

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
       
           
    def update_stock_historical_change(self, historicals, days, column_change, column_change_date ):
        change = historicals.change( days )
        sql = "update stocks set %s = %s, %s = '%s' where symbol = '%s'" % ( column_change, round_pct( change[1] ), column_change_date, change[0], historicals.symbol  )    
        self.cur.execute( sql )
        log.info( "SQL: %s" % ( sql ) )

    def update_stocks_historicals(self, log):
        self.cur.execute("select * from stocks")
        rows = self.cur.fetchall()   
    
        for row in rows:
            symbol = row['symbol']
            data_symbol = symbol
            if symbol == "BRKB":
                data_symbol = "BRK-B"
            log.info( "Downloading %s..." % ( data_symbol ) )
            try:
                data = historicals( data_symbol )
                self.update_stock_historical_change(data, data.CONST_BUSINESS_DAYS_ONE, "day_change", "day_change_date")    
                self.update_stock_historical_change(data, data.CONST_BUSINESS_DAYS_WEEK, "week_change", "week_change_date")    
                self.update_stock_historical_change(data, data.CONST_BUSINESS_DAYS_MONTH, "month_change", "month_change_date")    
                self.update_stock_historical_change(data, data.CONST_BUSINESS_DAYS_THREE_MONTHS, "three_month_change", "three_month_change_date")    
                self.update_stock_historical_change(data, data.CONST_BUSINESS_DAYS_YEAR, "year_change", "year_change_date")    
                self.update_stock_historical_change(data, data.CONST_BUSINESS_DAYS_FIVE_YEARS, "five_year_change", "five_year_change_date")    
                self.update_stock_historical_change(data, data.CONST_BUSINESS_DAYS_TEN_YEARS, "ten_year_change", "ten_year_change_date")                
                self.conn.commit()
                log.info( "Updated historicals for %s" % ( data_symbol ) )
            except Exception as err:
                log.error( "Could not get data for %s" % ( data_symbol ) )
                log.exception(err)
                continue


    
        
