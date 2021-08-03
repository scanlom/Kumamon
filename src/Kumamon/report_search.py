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
from api_blue_lion import cagr, confidence, headline_by_ticker, ref_data

CONST_CONFIDENCE_NONE           = 'NONE'
CONST_CONFIDENCE_HIGH           = 'HIGH'
CONST_CONFIDENCE_MEDIUM         = 'MEDIUM'
CONST_CONFIDENCE_LOW            = 'LOW'
CONST_CONFIDENCE_CONSTITUENT    = 'CONSTITUENT'

def populate_five_cagr( db, rpt ):
    log.info("populate_five_cagr called...")
    rows = db.session.query(db.Stocks).\
            filter(db.Stocks.hidden == False).\
            filter(db.Stocks.pe_terminal > 0).\
            all()
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_CONFIDENCE ]
    table = [ ]
    for row in rows:
        log.info("Requesting cagr for " + row.symbol)
        c = cagr(5, row.eps, row.payout, row.growth, row.pe_terminal, row.price)
        if c > Decimal(0.10):
            rowResearch = db.session.query(db.Researches).\
                filter(db.Researches.stock_id == row.id).\
                order_by(desc(db.Researches.id)).first()
            if rowResearch == None:
                table.append( [ row.symbol, c, CONST_CONFIDENCE_NONE ] )
            else:
                r = confidence(rowResearch.comment)
                # If it's a constituent, don't worry about the confidence
                rowConstituent = db.session.query(db.Constituents).\
                    filter(db.Constituents.stock_id == row.id).first()
                if rowConstituent != None:
                    r = CONST_CONFIDENCE_CONSTITUENT
                if r != CONST_CONFIDENCE_LOW:
                    table.append( [ row.symbol, c, r ] )
    if len(table) > 1:
        table.sort(key=lambda a : a[1],reverse=True)
        table.insert(0, [ "Symbol", "5yr CAGR", "Confidence" ])
        rpt.add_heading( "Watch List - 5yr CAGR > 10%" )
        rpt.add_table( table, formats )
    else:
        rpt.add_heading( "Watch List - 5yr CAGR > 10% - None" )

def populate_magic( rpt ):
    log.info("populate_magic called...")
    rpt.add_heading( "Screen - Magic Top Ten" )
    headlines = []
    instruments = ref_data()
    for i in instruments:
        log.info("Requesting headline for " + i['symbol'])
        headlines.append(headline_by_ticker( i['symbol'] ))
    sorted_headlines = sorted(headlines, reverse = True, key = lambda i: i['magic'])
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_CCY_COLOR ]
    table = [ ]
    table.append( [ "Ticker", "Description", "Magic" ] )
    for x in range(10):
        table.append( [sorted_headlines[x]['ticker'], sorted_headlines[x]['description'], sorted_headlines[x]['magic']] )
    rpt.add_table( table, formats )

def main():
    log.info("Started...")
    db = database2()
    rpt = report()
    
    populate_five_cagr( db, rpt )
    populate_magic( rpt )
  
    subject = 'Blue Lion - Search'
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")