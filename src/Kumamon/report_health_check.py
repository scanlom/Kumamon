'''
Created on Jul 14, 2013

@author: scanlom
'''

from datetime import datetime
from decimal import Decimal
from sqlalchemy.sql import func
from api_database import database2
from api_log import log
from api_mail import send_mail_html_self
from api_reporting import report
from api_blue_lion import cagr

def populate_five_cagr( db, rpt ):
    rows = db.session.query(db.Constituents, db.Stocks).\
            filter(db.Constituents.stock_id == db.Stocks.id).\
            filter(db.Constituents.portfolio_id == db.CONST_PORTFOLIO_PLAY).\
            filter(db.Constituents.pricing_type == db.CONST_PRICING_TYPE_BY_PRICE).\
            all()
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT_COLOR ]
    table = [ ]
    for row in rows:
        c = cagr(5, row.stocks.eps, row.stocks.payout, row.stocks.growth, row.stocks.pe_terminal, row.stocks.price)
        if c < Decimal(0.05):
            table.append( [ row.stocks.symbol, c ] )
    if len(table) > 0:
        table.sort(key=lambda a : a[1])
        table.insert(0, [ "Symbol", "5yr CAGR" ])
        rpt.add_string( "5yr CAGR < 5% - Sell" )
        rpt.add_table( table, formats )
    else:
        rpt.add_string( "5yr CAGR < 5% - OK" )

def populate_reds( db, rpt ):
    rows = db.session.query(db.Constituents).\
            filter(db.Constituents.portfolio_id == db.CONST_PORTFOLIO_PLAY).\
            filter(db.Constituents.pricing_type == db.CONST_PRICING_TYPE_BY_PRICE).\
            all()
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_NONE ]
    table = [ ]
    today = datetime.now().date()
    for row in rows:
        date = db.session.query(func.max(db.Researches.date)).\
            filter(db.Researches.stock_id == row.stock_id).\
            scalar()
        months = (today.year - date.year) * 12 + today.month - date.month
        if months > 3 or (months == 3 and today.day > date.day):    
            table.append( [ row.symbol, date ] )
    if len(table) > 0:
        table.sort(key=lambda a : a[1])
        table.insert(0, [ "Symbol", "Date" ])
        rpt.add_string( "Reds - Action" )
        rpt.add_table( table, formats )
    else:
        rpt.add_string( "Reds - OK" )

def populate_cash( db, rpt ):
    cash = db.get_constituents_by_portfolio_symbol( db.CONST_PORTFOLIO_CASH, db.CONST_SYMBOL_CASH )
    debt = -1*db.get_constituents_by_portfolio_symbol( db.CONST_PORTFOLIO_CASH, db.CONST_SYMBOL_DEBT  )
    cash_managed = db.get_constituents_by_portfolio_symbol( db.CONST_PORTFOLIO_MANAGED, db.CONST_SYMBOL_CASH )
    cash_play = db.get_constituents_by_portfolio_symbol( db.CONST_PORTFOLIO_PLAY, db.CONST_SYMBOL_CASH )
    total_rotc = db.get_balance( db.CONST_BALANCES_TYPE_TOTAL_ROTC )
    margin = debt + cash + cash_managed + cash_play

    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_CCY_COLOR, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_NONE ]
    table = [ 
        [ "Cash", "Value", "%" ],
        [ "Margin", margin, margin / total_rotc ],
        [ "Debt", debt, debt / total_rotc ],
        [ "Cash", cash, cash / total_rotc ],
        [ "Cash (Play)", cash_play, cash_play / total_rotc ],
        [ "Cash (Managed)", cash_managed, cash_managed / total_rotc ],
        ]
    rpt.add_string( "Cash - Aim for Fumi Red, Zero, Zero, Zero" )
    rpt.add_table( table, formats )
        
def populate_allocations( db, rpt ):
    total = db.get_balance( db.CONST_BALANCES_TYPE_TOTAL_ROTC )
    portfolio = db.get_balance( db.CONST_BALANCES_TYPE_TOTAL_SELF )
    play = db.get_balance( db.CONST_BALANCES_TYPE_TOTAL_PLAY )
    managed = db.get_balance( db.CONST_BALANCES_TYPE_TOTAL_MANAGED )
    cash = db.get_constituents_by_portfolio_symbol( db.CONST_PORTFOLIO_CASH, db.CONST_SYMBOL_CASH )
    oak_target = Decimal(0.20)
    play_target = Decimal(0.50)
    managed_target = Decimal(0.30)
    cash_target = Decimal(0.00)
    oak_off = ( portfolio - play ) / total - oak_target
    play_off = play / total - play_target
    managed_off = managed / total - managed_target
    cash_off = cash / total - cash_target
    
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_CCY_COLOR, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_PCT ]
    table = [ 
        [ "Allocation", "Value", "%", "Target" ],
        [ "Oak", oak_off * total, oak_off, oak_target ],
        [ "Play", play_off * total, play_off, play_target ],
        [ "Managed", managed_off * total, managed_off, managed_target ],
        [ "Cash", cash_off * total, cash_off, cash_target ],
        ]
    rpt.add_string( "Allocations - Aim for Zero" )
    rpt.add_table( table, formats )
    
def populate_thirty_pe( db, rpt ):
    rows = db.session.query(db.Stocks, db.Constituents).\
            filter(db.Constituents.stock_id == db.Stocks.id).\
            filter(db.Constituents.pricing_type == db.CONST_PRICING_TYPE_BY_PRICE).\
            filter(db.Constituents.portfolio_id == db.CONST_PORTFOLIO_PLAY).\
            all()
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_CCY ]
    table = [ ]
    for row in rows:
        if row.stocks.price / row.stocks.eps > 30:
            table.append( [ row.stocks.symbol, row.stocks.price / row.stocks.eps ] )
    if len(table) > 0:
        table.sort(key=lambda a : a[1],reverse=True)
        table.insert(0, [ "Symbol", "PE" ])
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

    rpt.add_heading("Trade")
    populate_cash(db, rpt)
    rpt.add_string("")        
    populate_allocations(db, rpt)
    rpt.add_heading("Upgrade")
    populate_thirty_pe( db, rpt )
    rpt.add_string("")        
    populate_five_cagr(db, rpt)
    rpt.add_heading("Research")
    populate_reds(db, rpt)
    rpt.add_string("")        
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