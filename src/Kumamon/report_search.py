'''
Created on Dec 8, 2019

@author: scanlom
'''

from decimal import Decimal
from sqlalchemy import desc
from sqlalchemy.sql import func
from api_database import database2
from api_log import log
from api_mail import send_mail_html_self
from api_reporting import report
from api_utils import cagr
from api_utils import confidence

CONST_CONFIDENCE_NONE   = 'NONE'
CONST_CONFIDENCE_HIGH   = 'HIGH'

def populate_five_cagr( db, rpt ):
    rows = db.session.query(db.Stocks, db.Constituents).\
            outerjoin(db.Constituents, db.Stocks.id == db.Constituents.stock_id).\
            filter(db.Constituents.stock_id == None).\
            filter(db.Stocks.hidden == False).\
            filter(db.Stocks.pe_terminal > 0).\
            all()
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT_COLOR ]
    table = [ ]
    for row in rows:
        log.info("Requesting cagr for " + row.stocks.symbol)
        c = cagr(5, row.stocks.eps, row.stocks.payout, row.stocks.growth, row.stocks.pe_terminal, row.stocks.price)
        if c > Decimal(0.10):
            rowResearch = db.session.query(db.Researches).\
                filter(db.Researches.stock_id == row.stocks.id).\
                order_by(desc(db.Researches.id)).first()
            if rowResearch == None:
                table.append( [ row.stocks.symbol, c ] )
            else:
                r = confidence(rowResearch.comment)
                if r == CONST_CONFIDENCE_HIGH or r == CONST_CONFIDENCE_NONE:
                    table.append( [ row.stocks.symbol, c ] )
    if len(table) > 1:
        table.sort(key=lambda a : a[1],reverse=True)
        table.insert(0, [ "Symbol", "5yr CAGR" ])
        rpt.add_string( "Watch List 5yr CAGR > 10%" )
        rpt.add_table( table, formats )
    else:
        rpt.add_string( "Watch List 5yr CAGR > 10% - None" )

def main():
    log.info("Started...")
    db = database2()
    rpt = report()
    
    populate_five_cagr( db, rpt )
  
    subject = 'Blue Lion - Search'
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")