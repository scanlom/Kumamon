'''
Created on Jul 14, 2013
@author: scanlom
'''

from datetime import datetime
from decimal import Decimal
from lib_log import log
from lib_mail import send_mail_html_self
from lib_reporting import report
from lib_constants import CONST
import lib_common as _common
import api_blue_lion as _abl

def populate_five_cagr( projections, rpt ):
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT_COLOR ]
    table = [ ]
    for p in projections:
        c = p['cagr5yr']
        if c < Decimal(0.05):
            table.append( [ p['ticker'], c ] )
    if len(table) > 0:
        table.sort(key=lambda a : a[1])
        table.insert(0, [ "Symbol", "5yr CAGR" ])
        rpt.add_string( "5yr CAGR < 5% - Sell" )
        rpt.add_table( table, formats )
    else:
        rpt.add_string( "5yr CAGR < 5% - OK" )

def populate_reds( projections, rpt ):
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_NONE ]
    table = [ ]
    today = datetime.now().date()
    for p in projections:
        date = _common.date_from_json(p)
        months = (today.year - date.year) * 12 + today.month - date.month
        if months > 3 or (months == 3 and today.day > date.day):    
            table.append( [ p['ticker'], date ] )
    if len(table) > 0:
        table.sort(key=lambda a : a[1])
        table.insert(0, [ "Symbol", "Date" ])
        rpt.add_string( "Reds - Action" )
        rpt.add_table( table, formats )
    else:
        rpt.add_string( "Reds - OK" )

def populate_cash( portfolios, rpt ):
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_CCY ]
    table = [ ]
    for port in portfolios:
        if port['cash'] > 0:    
            table.append( [ port['name'], port['cash'] ] )
    if len(table) > 0:
        table.insert(0, [ "Portfolio", "Cash" ])
        rpt.add_string( "Cash - Action" )
        rpt.add_table( table, formats )
    else:
        rpt.add_string( "Cash - OK" )
        
"""def populate_allocations( db, rpt ):
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
    rpt.add_table( table, formats )"""
    
def populate_thirty_pe( projections, rpt ):
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_CCY ]
    table = [ ]
    for p in projections:
        if p['pe'] > 30:
            table.append( [ p['ticker'], p['pe'] ] )
    if len(table) > 0:
        table.sort(key=lambda a : a[1],reverse=True)
        table.insert(0, [ "Symbol", "PE" ])
        rpt.add_string( "Thirty PE - Sell" )
        rpt.add_table( table, formats )                 
    else:
        rpt.add_string( "Thirty PE - OK" )

def populate_returns( returns, rpt ):
    rpt.add_string( "Selfie Returns - Monitor" )
    max_mover_columns = { "day_change": "day", "week_change": "week", "month_change": "month", "three_month_change": "3month", 
                         "year_change": "year", "five_year_change": "5year", "ten_year_change": "10year" }
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_PCT_COLOR, \
               rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_PCT_COLOR ]
    table = [ [ "Symbol", "Day", "Week", "Month", "3 Month", "Year", "5 Year", "10 Year" ] ]
    for r in returns:
        table.append( [ r['name'], r['oneDay'], r['oneWeek'], r['oneMonth'], r['threeMonths'], r['oneYear'], r['fiveYears'], r['tenYears'] ] )
    rpt.add_table( table, formats )

def main():
    log.info("Started...")

    rpt = report()
    projections = _abl.projections_positions()
    portfolios = _abl.portfolios()
    positions = _abl.enriched_positions_by_portfolio_id(CONST.PORTFOLIO_SELFIE)
    returns = []
    for pos in positions:
        returns.append(_abl.position_returns_by_id(pos['id']))

    rpt.add_heading("Trade")
    populate_cash(portfolios, rpt)
    rpt.add_string("")        
    #populate_allocations(db, rpt)
    rpt.add_heading("Upgrade")
    populate_thirty_pe(projections, rpt )
    rpt.add_string("")        
    populate_five_cagr(projections, rpt)
    rpt.add_heading("Research")
    populate_reds(projections, rpt)
    rpt.add_string("")        
    populate_returns( returns, rpt )
    
    subject = 'Blue Lion - Health Check'
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")