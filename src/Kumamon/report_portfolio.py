'''
Created on Jul 20, 2013

@author: scanlom
'''

from datetime import datetime
from decimal import Decimal
from math import log as math_log
from api_database import database2
from api_log import log
from api_mail import send_mail_html_self
from api_reporting import report

CONST_ONE_UNIT  = Decimal(211569.04)

def append_ytd_qtd_day( db, row, index ):
    cur = db.get_index_history(index, datetime.today().date())
    row.append(cur / db.get_index_history(index, db.get_ytd_base_date()) - 1)
    row.append(cur / db.get_index_history(index, db.get_qtd_base_date()) - 1)
    row.append(cur / db.get_index_history(index, db.get_day_base_date()) - 1)

def append_inflection_report( db, rpt, years, index_roe, total_roe ):    
    row_base_roe = db.get_index_history_minus_years(database2.CONST_INDEX_ROE, years)
    cagr = ( ( index_roe / row_base_roe.value ) ** Decimal( 1 / years ) ) - 1
    inflect = total_roe * cagr - CONST_ONE_UNIT
    font = ", <font color='green'>"
    if inflect <= 0:
        font = ", <font color='red'>"
    msg = str(years) + " Inflection - " + rpt.format_pct(cagr) + font + rpt.format_ccy( inflect ) + "</font> (" + str(row_base_roe.date) + ")"
    if inflect <= 0:
        msg += " " + rpt.format_ccy( math_log(CONST_ONE_UNIT / (total_roe * cagr), cagr + 1) )
    rpt.add_string(msg)

def main():
    log.info("Started...")
   
    db = database2()
    rpt = report()
    total_roe = db.get_balance(db.CONST_BALANCES_TYPE_TOTAL_ROE)
    index_roe = db.get_index_history(db.CONST_INDEX_ROE, datetime.today().date())
    ytd_base_index_roe = db.get_index_history(db.CONST_INDEX_ROE, db.get_ytd_base_date())
    
    # Determine cash made this year
    profit = total_roe - db.get_balance_history(db.CONST_BALANCES_TYPE_TOTAL_ROE, db.get_ytd_base_date()) - db.get_balance(db.CONST_BALANCES_TYPE_SAVINGS)

    # Send a summary mail
    subject = "Profit - " + rpt.format_ccy(profit) + " / " + rpt.format_pct(index_roe/ytd_base_index_roe - 1)
    
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT, rpt.CONST_FORMAT_PCT, rpt.CONST_FORMAT_PCT ]
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
    rpt.add_string("One Unit (" + rpt.format_ccy(CONST_ONE_UNIT) + ") - " + rpt.format_pct(CONST_ONE_UNIT / total_roe))
    rpt.add_string("One Million - " + rpt.format_pct(1000000 / total_roe))
    append_inflection_report(db, rpt, 5, index_roe, total_roe)
    append_inflection_report(db, rpt, 10, index_roe, total_roe)
    append_inflection_report(db, rpt, 15, index_roe, total_roe)
    append_inflection_report(db, rpt, 19, index_roe, total_roe)
    
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")