'''
Created on Aug 7, 2013

@author: scanlom
'''

from decimal import Decimal
from api_blue_lion import last
from api_database import database2
from lib_log import log

CONST_FX_GBP = Decimal(76.34)
CONST_FX_HKD = Decimal(7.79)
CONST_FX_ILS = Decimal(342)
CONST_FX_INR = Decimal(73.52)
CONST_FX_JPY = Decimal(104.01)
CONST_FX_SGD = Decimal(1.35)
CONST_FX_MAP = {
        "1373.HK": CONST_FX_HKD,
        "2788.HK": CONST_FX_HKD,
        "6670.T": CONST_FX_JPY,
        "ASALCBR.NS": CONST_FX_INR,
        "MRO.L": CONST_FX_GBP,
        "BATS.L": CONST_FX_GBP,
        "DWL.L": CONST_FX_GBP,
        "TEVA.TA": CONST_FX_ILS,
        "U11.SI": CONST_FX_SGD,
    }

def populate_price_and_value(db, rows, populate_value):
    for row in rows:
        log.info( "Downloading %s..." % ( row.symbol ) )
        fx = 1
        if row.symbol in CONST_FX_MAP:
            fx = CONST_FX_MAP[ row.symbol ]
            log.info( "Using fx %f" % ( fx ) )
        try:
            row.price = last( row.symbol )
            if populate_value:
                row.value = row.price * (Decimal(1) / fx) * row.quantity
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