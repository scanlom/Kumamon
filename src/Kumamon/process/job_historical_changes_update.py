'''
Created on Nov 30, 2013
@author: scanlom
'''

from Kumamon.load.api_analytics import get_market_data_symbol
from Kumamon.load.api_analytics import historicals
from Kumamon.common.api_database import database2
from lib_log import log

def update_stock_historical_change(row, historicals, days, column_change, column_change_date):
    change = historicals.change(days)
    setattr(row, column_change_date, change[0])
    setattr(row, column_change, change[1])

def main():
    log.info("Started...")
    db = database2()
    rows = db.get_stocks()
    for row in rows:
        log.info( "Downloading %s..." % ( row.symbol ) )
        try:
            h = historicals( get_market_data_symbol( row.symbol ) )
            update_stock_historical_change(row, h, h.CONST_BUSINESS_DAYS_ONE, "day_change", "day_change_date")    
            update_stock_historical_change(row, h, h.CONST_BUSINESS_DAYS_WEEK, "week_change", "week_change_date")    
            update_stock_historical_change(row, h, h.CONST_BUSINESS_DAYS_MONTH, "month_change", "month_change_date")    
            update_stock_historical_change(row, h, h.CONST_BUSINESS_DAYS_THREE_MONTHS, "three_month_change", "three_month_change_date")    
            update_stock_historical_change(row, h, h.CONST_BUSINESS_DAYS_YEAR, "year_change", "year_change_date")    
            update_stock_historical_change(row, h, h.CONST_BUSINESS_DAYS_FIVE_YEARS, "five_year_change", "five_year_change_date")    
            update_stock_historical_change(row, h, h.CONST_BUSINESS_DAYS_TEN_YEARS, "ten_year_change", "ten_year_change_date")                
        except Exception as err:
            # Log exceptions as warnings, there often won't be historical data for international names
            log.warning( "Could not get data for %s" % ( row.symbol ) )
            # log.exception(err)
            continue   

    log.info( "Committing transaction..." )
    db.commit()
    
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")