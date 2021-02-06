'''
Created on May 15, 2019

@author: scanlom
'''

from datetime import date
from datetime import datetime
from datetime import timedelta
from api_database import database2
from api_log import log
from api_mail import send_mail_html_self
from api_reporting import report

def main():
    log.info("Started...")
    db = database2()
    rpt = report()
        
    CONST_PORTFOLIO = 1
    CONST_START = date(2020,1,21)
    CONST_END = date(2017,1,1)
    
    contributors = {}
    start = db.get_portfolio_history_by_date(CONST_PORTFOLIO,CONST_START)
    for row in start:
        contributors[ row.symbol ] = [ row.symbol, row.value, 0, 0, 0, 0, 0, 0 ]
    end = db.get_portfolio_history_by_date(CONST_PORTFOLIO,CONST_END)    
    for row in end:
        if row.symbol in contributors:
            contributors[ row.symbol ][ 5 ] = row.value
        else:
            contributors[ row.symbol ] = [ row.symbol, 0, 0, 0, 0, row.value, 0, 0 ]
    divs = db.get_actions_by_date_range_type(CONST_START, CONST_END, db.CONST_ACTION_TYPE_DIVIDEND_PORTFOLIO )
    for row in divs:
        if row.symbol in contributors:
            contributors[ row.symbol ][ 4 ] += row.value1
    buys = db.get_actions_by_date_range_type(CONST_START, CONST_END, db.CONST_ACTION_TYPE_BOUGHT_PORTFOLIO )
    for row in buys:
        if row.symbol in contributors:
            contributors[ row.symbol ][ 2 ] += row.value1     
    sells = db.get_actions_by_date_range_type(CONST_START, CONST_END, db.CONST_ACTION_TYPE_SOLD_PORTFOLIO )
    for row in sells:
        if row.symbol in contributors:
            contributors[ row.symbol ][ 3 ] += row.value1     
    for key, value in contributors.items():
        value[ 6 ] = value[ 3 ] + value[ 4 ] + value[ 5 ] - value[ 1 ] - value[ 2 ]
        value[ 7 ] = (value[ 1 ] + value[ 2 ] + value[6]) / (value[ 1 ] + value[ 2 ]) - 1
            
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY_COLOR, rpt.CONST_FORMAT_PCT_COLOR ]
    table = []
    for key, value in contributors.items():
        table.append( value )
    table.sort(key=lambda a : a[7]*-1)
    table.insert(0, [ "Symbol", "Start", "Buy", "Sell", "Div", "End", "Diff", "%" ])
    rpt.add_table( table, formats )

    subject = 'Blue Lion - Contributors'
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 