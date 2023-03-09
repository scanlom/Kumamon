'''
Created on May 15, 2019
@author: scanlom
'''

from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from math import inf
from api_database import database2
from lib_log import log
from lib_mail import send_mail_html_self
from lib_reporting import report

def populate_worst_best(db, rpt, date_start, date_end):
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_NONE ]
    table = [ [ "Period", "%", "Start", "End" ] ]
    for years in [1,3,5,10]:
        date_cur = date_end
        max_pct_down = inf    # And I think to myself...what a wonderful world
        max_pct_up = -inf
        max_pct_down_date_start = max_pct_up_date_start = date_start
        max_pct_down_date_end = max_pct_up_date_end = date_end
        while date_start < date_cur - timedelta(days=years*database2.CONST_DAYS_IN_YEAR):
            try:
                value_end = db.get_index_history(5, date_cur)
                row_start = db.get_index_history_minus_years_from_date(5, years, date_cur)
                pct_change = value_end / row_start.value - 1
                if pct_change < max_pct_down:
                    max_pct_down = pct_change
                    max_pct_down_date_start = row_start.date
                    max_pct_down_date_end = date_cur
                if pct_change > max_pct_up:
                    max_pct_up = pct_change
                    max_pct_up_date_start = row_start.date
                    max_pct_up_date_end = date_cur
                date_cur -= timedelta(days=1)
            except Exception as err:
                date_cur -= timedelta(days=1)
        max_pct_up = ( ( max_pct_up + 1 ) ** Decimal( 1 / years ) ) - 1
        max_pct_down = ( ( max_pct_down + 1 ) ** Decimal( 1 / years ) ) - 1
        table.append( [ str(years) + " Up", max_pct_up, max_pct_up_date_start, max_pct_up_date_end ] )
        table.append( [ str(years) + " Down", max_pct_down, max_pct_down_date_start, max_pct_down_date_end ] )
    rpt.add_table( table, formats )

def populate_contributors(db, rpt, start, end):
    CONST_PORTFOLIO = 5
    
    contributors = {}
    constituents_start = db.get_portfolio_history_by_date(CONST_PORTFOLIO,start)
    for row in constituents_start:
        contributors[ row.symbol ] = [ row.symbol, row.value, 0, 0, 0, 0, 0, 0 ]
    constituents_end = db.get_portfolio_history_by_date(CONST_PORTFOLIO,end)    
    for row in constituents_end:
        if row.symbol in contributors:
            contributors[ row.symbol ][ 5 ] = row.value
        else:
            contributors[ row.symbol ] = [ row.symbol, 0, 0, 0, 0, row.value, 0, 0 ]
    divs = db.get_actions_by_date_range_type(start, end, db.CONST_ACTION_TYPE_DIVIDEND_PLAY )
    for row in divs:
        if row.symbol in contributors:
            contributors[ row.symbol ][ 4 ] += row.value1
    buys = db.get_actions_by_date_range_type(start, end, db.CONST_ACTION_TYPE_BOUGHT_PLAY )
    for row in buys:
        if row.symbol in contributors:
            contributors[ row.symbol ][ 2 ] += row.value1     
    sells = db.get_actions_by_date_range_type(start, end, db.CONST_ACTION_TYPE_SOLD_PLAY )
    for row in sells:
        if row.symbol in contributors:
            contributors[ row.symbol ][ 3 ] += row.value1     
    for key, value in contributors.items():
        value[ 6 ] = value[ 3 ] + value[ 4 ] + value[ 5 ] - value[ 1 ] - value[ 2 ]
        if (value[ 1 ] + value[ 2 ]) > 0:
            value[ 7 ] = (value[ 1 ] + value[ 2 ] + value[6]) / (value[ 1 ] + value[ 2 ]) - 1
            
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY_COLOR, rpt.CONST_FORMAT_PCT_COLOR ]
    table = []
    for key, value in contributors.items():
        table.append( value )
    table.sort(key=lambda a : a[7]*-1)
    table.insert(0, [ "Symbol", "Start", "Buy", "Sell", "Div", "End", "Diff", "%" ])
    rpt.add_table( table, formats )

def main():
    log.info("Started...")
    db = database2()
    rpt = report()

    date_start = date(2022,1,1) #db.get_index_history_min_date(5)
    date_end = date(2023,1,1) #db.get_index_history_max_date(5)

    #populate_worst_best(db, rpt, date_start, date_end)

    rpt.add_heading("Contributors")
    populate_contributors(db, rpt, date_start, date_end)

    subject = 'Blue Lion - One Pager'
    print(rpt.get_html())
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 