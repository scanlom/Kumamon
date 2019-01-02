'''
Created on Jul 20, 2013

@author: scanlom
'''

from datetime import datetime
from decimal import Decimal
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
    
    row_base_roe_5 = db.get_index_history_minus_years(database2.CONST_INDEX_ROE, 5)
    row_base_roe_10 = db.get_index_history_minus_years(database2.CONST_INDEX_ROE, 10)
    cagr_five = ( ( index_roe / row_base_roe_5.value ) ** Decimal(0.2) ) - 1
    cagr_ten = ( ( index_roe / row_base_roe_10.value ) ** Decimal(0.1) ) - 1
    inflect_five = total_roe * cagr_five - CONST_ONE_UNIT
    inflect_ten = total_roe * cagr_ten - CONST_ONE_UNIT
    font = ", <font color='green'>"
    if inflect_five <= 0:
        font = ", <font color='red'>"
    rpt.add_string("Five Inflection - " + rpt.format_pct(cagr_five) + font + rpt.format_ccy( inflect_five ) + "</font> (" + str(row_base_roe_5.date) + ")")
    font = ", <font color='green'>"
    if inflect_ten <= 0:
        font = ", <font color='red'>"
    rpt.add_string("Ten Inflection - " + rpt.format_pct(cagr_ten) + font + rpt.format_ccy( inflect_ten ) + "</font> (" + str(row_base_roe_10.date) + ")")
    
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")