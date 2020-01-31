'''
Created on Jul 20, 2013

@author: scanlom
'''

from datetime import date
from datetime import datetime
from decimal import Decimal
from math import log as math_log
from api_database import database2
from api_log import log
from api_mail import send_mail_html_self
from api_reporting import report

CONST_ONE_UNIT      = Decimal(237251)
CONST_FINISH_PCT    = Decimal(0.04)
CONST_TEN_MILLION   = Decimal(10000000)
CONST_FINISH_DATE   = date(2035,4,17)

def append_ytd_qtd_day( db, row, index ):
    cur = db.get_index_history(index, datetime.today().date())
    row.append(cur / db.get_index_history(index, db.get_ytd_base_date()) - 1)
    row.append(cur / db.get_index_history(index, db.get_qtd_base_date()) - 1)
    row.append(cur / db.get_index_history(index, db.get_day_base_date()) - 1)

def append_inflection_report( db, row, years, index_roe, total_roe, total_finish ):
    row_base_roe = db.get_index_history_minus_years(database2.CONST_INDEX_ROE, years)
    cagr = ( ( index_roe / row_base_roe.value ) ** Decimal( 1 / years ) ) - 1
    inflect = total_roe * cagr - CONST_ONE_UNIT
    inflect_years = math_log(CONST_ONE_UNIT / (total_roe * cagr), cagr + 1)
    four_pct_years = math_log( total_finish / total_roe, cagr + 1 )
    ten_m_years = math_log( CONST_TEN_MILLION / total_roe, cagr + 1 )
    row.append( cagr )
    row.append( inflect )
    row.append( inflect_years * -1 )
    row.append( four_pct_years * -1 )
    row.append( ten_m_years * -1 )
    row.append( row_base_roe.date )

def main():
    log.info("Started...")
   
    db = database2()
    rpt = report()
    total_roe = db.get_balance(db.CONST_BALANCES_TYPE_TOTAL_ROE)
    total_finish = CONST_ONE_UNIT / CONST_FINISH_PCT 
    index_roe = db.get_index_history(db.CONST_INDEX_ROE, datetime.today().date())
    ytd_base_index_roe = db.get_index_history(db.CONST_INDEX_ROE, db.get_ytd_base_date())
    retirement_years = CONST_FINISH_DATE - datetime.today().date()
    
    # Determine cash made this year
    profit = total_roe - db.get_balance_history(db.CONST_BALANCES_TYPE_TOTAL_ROE, db.get_ytd_base_date()) - db.get_balance(db.CONST_BALANCES_TYPE_SAVINGS)

    # Send a summary mail
    subject = "Blue Lion - " + rpt.format_ccy(profit) + " / " + rpt.format_pct(index_roe/ytd_base_index_roe - 1)
    
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_PCT_COLOR ]
    table = [
        [ "", "YTD", "QTD", "Day" ],
        [ "Total (ROE)" ],
        [ "Total (ROTC)" ],
        [ "Self" ],
        [ "Play" ],
        [ "Managed" ],
        ]
    append_ytd_qtd_day( db, table[1], db.CONST_INDEX_ROE )
    append_ytd_qtd_day( db, table[2], db.CONST_INDEX_ROTC )
    append_ytd_qtd_day( db, table[3], db.CONST_INDEX_SELF )
    append_ytd_qtd_day( db, table[4], db.CONST_INDEX_PLAY )
    append_ytd_qtd_day( db, table[5], db.CONST_INDEX_MANAGED )
    rpt.add_table(table, formats)

    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT, rpt.CONST_FORMAT_CCY_INT_COLOR, rpt.CONST_FORMAT_CCY_COLOR, rpt.CONST_FORMAT_CCY_COLOR, rpt.CONST_FORMAT_CCY_COLOR, rpt.CONST_FORMAT_DATE_SHORT]
    table = [
        [ "", "%", "Inf", "Y", "4%Y", "10mY", "Date" ],
        [ "5" ],
        [ "10" ],
        [ "15" ],
        [ "20" ],
        ]
    append_inflection_report(db, table[1], 5, index_roe, total_roe, total_finish)    
    append_inflection_report(db, table[2], 10, index_roe, total_roe, total_finish)    
    append_inflection_report(db, table[3], 15, index_roe, total_roe, total_finish)    
    append_inflection_report(db, table[4], 20, index_roe, total_roe, total_finish)    
    rpt.add_table(table, formats)

    rpt.add_string("One Unit (" + rpt.format_ccy(CONST_ONE_UNIT) + ") - " + rpt.format_pct(CONST_ONE_UNIT / total_roe))
    rpt.add_string("One Million - " + rpt.format_pct(1000000 / total_roe))
    rpt.add_string("Net Worth - " + rpt.format_ccy( total_roe ))
    rpt.add_string("Four Percent - " + rpt.format_ccy( total_finish ))
    rpt.add_string("Retirement (Years) - " + rpt.format_ccy( retirement_years.days / 365.25 ))
    
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")