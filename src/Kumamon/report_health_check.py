'''
Created on Jul 14, 2013

@author: scanlom
'''

from datetime import datetime
from decimal import Decimal
from time import localtime
from time import strftime
from sqlalchemy.sql import func
from api_database import database2
from api_log import log
from api_mail import send_mail_html_self
from api_reporting import report
from api_utils import cagr

def populate_five_cagr( db, rpt ):
    rows = db.session.query(db.Constituents, db.Stocks).\
            filter(db.Constituents.stock_id == db.Stocks.id).\
            filter(db.Constituents.portfolio_id == db.CONST_PORTFOLIO_PLAY).\
            filter(db.Constituents.pricing_type == db.CONST_PRICING_TYPE_BY_PRICE).\
            all()
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT_COLOR ]
    table = [ [ "Symbol", "5yr CAGR" ] ]
    for row in rows:
        c = cagr(5, row.stocks.eps, row.stocks.payout, row.stocks.growth, row.stocks.pe_terminal, row.stocks.price)
        if c < Decimal(0.05):
            table.append( [ row.stocks.symbol, c ] )
    if len(table) > 1:
        rpt.add_string( "5yr CAGR < 5% - Sell" )
        rpt.add_table( table, formats )
    else:
        rpt.add_string( "5yr CAGR < 5% - " )

def populate_reds( db, rpt ):
    rows = db.session.query(db.Constituents).\
            filter(db.Constituents.portfolio_id == db.CONST_PORTFOLIO_PLAY).\
            filter(db.Constituents.pricing_type == db.CONST_PRICING_TYPE_BY_PRICE).\
            all()
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_NONE ]
    table = [ [ "Symbol", "Date" ] ]
    today = datetime.now().date()
    for row in rows:
        date = db.session.query(func.max(db.Researches.date)).\
            filter(db.Researches.stock_id == row.stock_id).\
            scalar()
        months = (today.year - date.year) * 12 + today.month - date.month
        if months >= 3:    
            table.append( [ row.symbol, date ] )
    if len(table) > 1:
        rpt.add_string( "Reds - Action" )
        rpt.add_table( table, formats )
    else:
        rpt.add_string( "Reds - OK" )

def populate_cash( db, rpt ):
    cash = db.session.query(func.sum(db.Constituents.value)).\
            filter(db.Constituents.symbol == db.CONST_SYMBOL_CASH).\
            filter(db.Constituents.portfolio_id != db.CONST_PORTFOLIO_PLAY).\
            scalar()
    debt = db.session.query(func.sum(db.Constituents.value)).\
            filter(db.Constituents.symbol == db.CONST_SYMBOL_DEBT).\
            filter(db.Constituents.portfolio_id != db.CONST_PORTFOLIO_PLAY).\
            scalar()
    recon = cash - debt
    if recon > 0:
        rpt.add_string( "Cash - Buy - " + rpt.format_ccy(recon) )
    else:
        rpt.add_string( "Cash - OK - " + rpt.format_ccy(recon) )

def populate_thirty_pe( db, rpt ):
    rows = db.session.query(db.Stocks, db.Constituents).\
            filter(db.Constituents.stock_id == db.Stocks.id).\
            filter(db.Constituents.pricing_type == db.CONST_PRICING_TYPE_BY_PRICE).\
            filter(db.Constituents.portfolio_id == db.CONST_PORTFOLIO_PLAY).\
            all()
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_CCY ]
    table = [ [ "Symbol", "PE" ] ]
    for row in rows:
        if row.stocks.price / row.stocks.eps > 30:
            table.append( [ row.stocks.symbol, row.stocks.price / row.stocks.eps ] )
    if len(table) > 1:
        rpt.add_string( "Thirty PE - Sell" )
        rpt.add_table( table, formats )                 
    else:
        rpt.add_string( "Thirty PE - OK" )

def populate_max_movers( db, rpt ):
    rpt.add_string( "Max Movers - Monitor" )
    max_mover_columns = { "day_change": "day", "week_change": "week", "month_change": "month", "three_month_change": "3month", 
                         "year_change": "year", "five_year_change": "5year", "ten_year_change": "10year" }
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_NONE ]
    table = [ [ "", "Symbol", "Move", "Date" ] ]
    for col in max_mover_columns:
        name = max_mover_columns[col]
        row = db.session.query(db.Stocks, db.Constituents).\
            filter(db.Constituents.stock_id == db.Stocks.id).\
            filter(db.Constituents.portfolio_id == db.CONST_PORTFOLIO_PLAY).\
            order_by(db.Stocks.__table__.columns[col].desc()).\
            first().stocks
        table.append( [ name + "_up", row.symbol, getattr(row, col), getattr(row, col + "_date" ) ] )
        row = db.session.query(db.Stocks, db.Constituents).\
            filter(db.Constituents.stock_id == db.Stocks.id).\
            filter(db.Constituents.portfolio_id == db.CONST_PORTFOLIO_PLAY).\
            order_by(db.Stocks.__table__.columns[col].asc()).\
            first().stocks
        table.append( [ name + "_down", row.symbol, getattr(row, col), getattr(row, col + "_date" ) ] )
    rpt.add_table( table, formats )

def main():
    log.info("Started...")
    db = database2()
    rpt = report()
    
    populate_reds(db, rpt)
    populate_cash(db, rpt)
    populate_thirty_pe( db, rpt )
    populate_five_cagr(db, rpt)
    populate_max_movers( db, rpt )
    
    subject = 'Blue Lion - Health Check'
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")