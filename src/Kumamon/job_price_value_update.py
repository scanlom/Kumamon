'''
Created on Aug 7, 2013

@author: scanlom
'''

from api_analytics import get_market_data_symbol
from api_analytics import last
from api_database import database2
from api_log import log
from api_mail import send_mail_html_self

def populate_price_and_value(db, rows, populate_value):
    for row in rows:
        log.info( "Downloading %s..." % ( row.symbol ) )
        try:
            row.price = last( get_market_data_symbol( row.symbol ) )
            if populate_value:
                row.value = row.price * row.quantity
            log.info( "Updated %s..." % ( row.symbol ) )
        except Exception as err:
            log.error( "Could not get price for %s" % ( row.symbol ) )
            log.exception(err)
            continue    
        
    log.info( "Committing transaction..." )
    db.commit()
    log.info( "Done" )

def main():
    log.info("Started loading prices for constituents...")
    db = database2()    
    rows = db.get_constituents(db.CONST_PRICING_TYPE_BY_PRICE)   
    populate_price_and_value(db, rows, True)
    log.info("Completed")

    log.info("Started loading prices for stocks...")
    rows = db.get_stocks()   
    populate_price_and_value(db, rows, False)
    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
        send_mail_html_self("FAILURE:  job_price_value_update.py", str( err ) ) 