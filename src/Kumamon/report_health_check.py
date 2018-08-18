'''
Created on Jul 14, 2013

@author: scanlom
'''

from time import localtime
from time import strftime
from api_database import database2
from api_log import log
from api_mail import send_mail_html_self
from api_reporting import report

def populate_max_movers( db, rpt ):
    rpt.add_string( "Max Movers" )
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_NONE ]
    table = [ [ "", "Symbol", "Move", "Date" ] ]
    for col in [ "day_change", "week_change", "month_change", "three_month_change", "year_change", "five_year_change", "ten_year_change" ]:
        row = db.session.query(db.Stocks, db.Constituents).\
            filter(db.Constituents.stock_id == db.Stocks.id).\
            filter(db.Constituents.portfolio_id == db.CONST_PORTFOLIO_PLAY).\
            order_by(db.Stocks.__table__.columns[col].desc()).\
            first().stocks
        table.append( [ col + "_up", row.symbol, getattr(row, col), getattr(row, col + "_date" ) ] )
        row = db.session.query(db.Stocks, db.Constituents).\
            filter(db.Constituents.stock_id == db.Stocks.id).\
            filter(db.Constituents.portfolio_id == db.CONST_PORTFOLIO_PLAY).\
            order_by(db.Stocks.__table__.columns[col].asc()).\
            first().stocks
        table.append( [ col + "_down", row.symbol, getattr(row, col), getattr(row, col + "_date" ) ] )
    rpt.add_table( table, formats )

def main():
    log.info("Started...")
    db = database2()
    rpt = report()
    
    populate_max_movers( db, rpt )
    subject = 'Health Check - ' + strftime("%Y-%m-%d", localtime())
     
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")