'''
Created on Jul 20, 2013
@author: scanlom
'''

from datetime import date
from datetime import datetime
from decimal import Decimal
from math import log as math_log
from lib_constants import CONST
from api_database import database2
from lib_log import log
from lib_mail import send_mail_html_self
from lib_reporting import report

def append_ytd_qtd_day( db, row, index ):
    cur = db.get_index_history(index, datetime.today().date())
    row.append(cur / db.get_index_history(index, db.get_ytd_base_date()) - 1)
    row.append(cur / db.get_index_history(index, db.get_qtd_base_date()) - 1)
    row.append(cur / db.get_index_history(index, db.get_day_base_date()) - 1)

def calculate_years_for_value(finish, start, cagr, spending):
    years = 0
    current = start
    while finish > current:
        years += 1
        current += current * (cagr) - spending
        if current < start:
            return float("NaN")
    return years

def append_inflection_report( db, row, years, index_roe, total_roe, total_finish, spending ):
    row_base_roe = db.get_index_history_minus_years(database2.CONST_INDEX_ROE, years)
    cagr = ( ( index_roe / row_base_roe.value ) ** Decimal( 1 / years ) ) - 1
    inflect = five_m_years = four_pct_years = float("NaN")
    if cagr > 0:
        inflect = total_roe * cagr
        four_pct_years = calculate_years_for_value(total_finish, total_roe, cagr, spending)
        five_m_years = calculate_years_for_value(CONST.FIVE_MILLION, total_roe, cagr, spending)
    row.append( cagr )
    row.append( inflect )
    row.append( five_m_years * -1 )
    row.append( four_pct_years * -1 )
    row.append( row_base_roe.date )

def populate_summary(db, rpt, index_roe, total_roe, total_finish, profit, spending):
    rpt.add_heading("Summary")
    
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_PCT_COLOR ]
    table = [
        [ "", "YTD", "QTD", "Day" ],
        [ "Total (ROE)" ],
        [ "Total (ROTC)" ],
        [ "Play" ],
        [ "Oak" ],
        [ "Managed" ],
        [ "Risk Arb" ],
        [ "Trade Fin" ],
        [ "Quick" ],
        ]
    append_ytd_qtd_day( db, table[1], db.CONST_INDEX_ROE )
    append_ytd_qtd_day( db, table[2], db.CONST_INDEX_ROTC )
    append_ytd_qtd_day( db, table[3], db.CONST_INDEX_PLAY )
    append_ytd_qtd_day( db, table[4], db.CONST_INDEX_OAK )
    append_ytd_qtd_day( db, table[5], db.CONST_INDEX_MANAGED )
    append_ytd_qtd_day( db, table[6], db.CONST_INDEX_RISK_ARB )
    append_ytd_qtd_day( db, table[7], db.CONST_INDEX_TRADE_FIN )
    append_ytd_qtd_day( db, table[8], db.CONST_INDEX_QUICK )
    rpt.add_table(table, formats)

    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT, rpt.CONST_FORMAT_CCY_INT_COLOR, rpt.CONST_FORMAT_YEARS, rpt.CONST_FORMAT_YEARS, rpt.CONST_FORMAT_DATE_SHORT]
    table = [
        [ "", "%", "Inf", "5mY", "4%Y", "Date" ],
        [ "5" ],
        [ "10" ],
        [ "15" ],
        [ "20" ],
        ]
    append_inflection_report(db, table[1], 5, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(db, table[2], 10, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(db, table[3], 15, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(db, table[4], 20, index_roe, total_roe, total_finish, spending)    
    rpt.add_table(table, formats)

    rpt.add_string("One Unit (" + rpt.format_ccy(CONST.BUDGET_GROSS) + ") - " + rpt.format_pct(CONST.BUDGET_GROSS / total_roe))
    rpt.add_string("One Million - " + rpt.format_pct(1000000 / total_roe))
    rpt.add_string("Net Worth - " + rpt.format_ccy( total_roe ))
    rpt.add_string("Four Percent - " + rpt.format_ccy( total_finish ))
    rpt.add_string("Since Inception (Beat %11.11) - " + rpt.format_pct( ( ( index_roe / CONST.INCEPT_INDEX ) ** Decimal( 1 / ((datetime.today().date()-CONST.INCEPT_DATE).days / 365.25) ) ) - 1 )
        + " (" + rpt.format_ccy(index_roe) + " / " + rpt.format_ccy(CONST.INCEPT_INDEX) + ", " + rpt.format_ccy(((datetime.today().date()-CONST.INCEPT_DATE).days / 365.25)) + " years)")

def populate_stress_test_twenty_percent_drop(db, rpt, index_roe, total_roe, total_finish, spending):
    rpt.add_heading("Stress Test - 20% Drop")
    index_roe *= Decimal(0.8)
    total_roe *= Decimal(0.8)
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT, rpt.CONST_FORMAT_CCY_INT_COLOR, rpt.CONST_FORMAT_YEARS, rpt.CONST_FORMAT_YEARS, rpt.CONST_FORMAT_DATE_SHORT]
    table = [
        [ "", "%", "Inf", "5mY", "4%Y", "Date" ],
        [ "5" ],
        [ "10" ],
        [ "15" ],
        [ "20" ],
        ]
    append_inflection_report(db, table[1], 5, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(db, table[2], 10, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(db, table[3], 15, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(db, table[4], 20, index_roe, total_roe, total_finish, spending)    
    rpt.add_table(table, formats)

def populate_stress_test_fifty_percent_drop_from_max(db, rpt, index_roe_max, index_roe, total_roe, total_finish, spending):
    rpt.add_heading("Stress Test - 50% Drop From Max")
    factor = (index_roe_max * Decimal(0.5)) / index_roe 
    index_roe *= Decimal(factor)
    total_roe *= Decimal(factor)
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT, rpt.CONST_FORMAT_CCY_INT_COLOR, rpt.CONST_FORMAT_YEARS, rpt.CONST_FORMAT_YEARS, rpt.CONST_FORMAT_DATE_SHORT]
    table = [
        [ "", "%", "Inf", "5mY", "4%Y", "Date" ],
        [ "5" ],
        [ "10" ],
        [ "15" ],
        [ "20" ],
        ]
    append_inflection_report(db, table[1], 5, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(db, table[2], 10, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(db, table[3], 15, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(db, table[4], 20, index_roe, total_roe, total_finish, spending)    
    rpt.add_table(table, formats)
    rpt.add_string( "Factor " + rpt.format_pct(factor) + " CNW " + rpt.format_ccy(total_roe) )
    
def main():
    log.info("Started...")
   
    db = database2()
    rpt = report()
    total_roe = db.get_balance(db.CONST_BALANCES_TYPE_TOTAL_ROE)
    total_finish = CONST.BUDGET_GROSS / CONST.PLAN_FINISH_PCT 
    index_roe = db.get_index_history(db.CONST_INDEX_ROE, datetime.today().date())
    index_roe_max = db.get_index_max(db.CONST_INDEX_ROE)
    ytd_base_index_roe = db.get_index_history(db.CONST_INDEX_ROE, db.get_ytd_base_date())
    
    # Determine cash made this year
    profit = total_roe - db.get_balance_history(db.CONST_BALANCES_TYPE_TOTAL_ROE, db.get_ytd_base_date()) - db.get_balance(db.CONST_BALANCES_TYPE_SAVINGS)

    populate_summary(db, rpt, index_roe, total_roe, total_finish, profit, CONST.BUDGET_GROSS)
    populate_stress_test_twenty_percent_drop(db, rpt, index_roe, total_roe, total_finish, CONST.BUDGET_GROSS)
    populate_stress_test_fifty_percent_drop_from_max(db, rpt, index_roe_max, index_roe, total_roe, total_finish, CONST.BUDGET_GROSS)
    
    # Send a summary mail
    subject = "Blue Lion - " + rpt.format_ccy(profit) + " / " + rpt.format_pct(index_roe/ytd_base_index_roe - 1)
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")