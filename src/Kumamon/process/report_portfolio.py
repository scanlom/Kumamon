'''
Created on Jul 20, 2013
@author: scanlom
'''

from datetime import datetime
from datetime import timedelta
from lib_constants import CONST
import api_blue_lion as _abl
import lib_common as _common
from lib_log import log
from lib_mail import send_mail_html_self
from lib_reporting import report

def get_index_history_minus_years( id, years ):
    date = datetime.now().date() - timedelta(days=years*CONST.DAYS_IN_YEAR)
    return _abl.portfolios_history_by_portfolio_id_date(id, date)

def append_ytd_qtd_day( row, id, field ):
    cur = _abl.portfolios_history_by_portfolio_id_date(id, datetime.today().date())[field]
    row.append(cur / _abl.portfolios_history_by_portfolio_id_date(id, _common.get_ytd_base_date())[field] - 1)
    row.append(cur / _abl.portfolios_history_by_portfolio_id_date(id, _common.get_qtd_base_date())[field] - 1)
    row.append(cur / _abl.portfolios_history_by_portfolio_id_date(id, _common.get_day_base_date())[field] - 1)

def calculate_years_for_value(finish, start, cagr, spending):
    years = 0
    current = start
    while finish > current:
        years += 1
        current += current * (cagr) - spending
        if current < start:
            return float("NaN")
    return years

def append_inflection_report( row, years, index_roe, total_roe, total_finish, spending ):
    json_base_roe = get_index_history_minus_years(CONST.PORTFOLIO_TOTAL, years)
    cagr = ( ( index_roe / json_base_roe['index'] ) ** ( 1 / years ) ) - 1
    inflect = five_m_years = four_pct_years = float("NaN")
    if cagr > 0:
        inflect = total_roe * cagr
        four_pct_years = calculate_years_for_value(total_finish, total_roe, cagr, spending)
        five_m_years = calculate_years_for_value(CONST.FIVE_MILLION, total_roe, cagr, spending)
    row.append( cagr )
    row.append( inflect )
    row.append( five_m_years * -1 )
    row.append( four_pct_years * -1 )
    row.append( datetime.strptime(json_base_roe['date'][:10], '%Y-%m-%d') )

def populate_summary(rpt, index_roe, total_roe, total_finish, spending):
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
    append_ytd_qtd_day( table[1], CONST.PORTFOLIO_TOTAL, 'index' )
    append_ytd_qtd_day( table[2], CONST.PORTFOLIO_TOTAL, 'indexTotalCapital')
    append_ytd_qtd_day( table[3], CONST.PORTFOLIO_SELFIE, 'index' )
    append_ytd_qtd_day( table[4], CONST.PORTFOLIO_OAK, 'index' )
    append_ytd_qtd_day( table[5], CONST.PORTFOLIO_MANAGED, 'index' )
    append_ytd_qtd_day( table[6], CONST.PORTFOLIO_RISK_ARB, 'index' )
    append_ytd_qtd_day( table[7], CONST.PORTFOLIO_TRADE_FIN, 'index' )
    append_ytd_qtd_day( table[8], CONST.PORTFOLIO_QUICK, 'index' )
    rpt.add_table(table, formats)

    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT, rpt.CONST_FORMAT_CCY_INT_COLOR, rpt.CONST_FORMAT_YEARS, rpt.CONST_FORMAT_YEARS, rpt.CONST_FORMAT_DATE_SHORT]
    table = [
        [ "", "%", "Inf", "5mY", "4%Y", "Date" ],
        [ "5" ],
        [ "10" ],
        [ "15" ],
        [ "20" ],
        ]
    append_inflection_report(table[1], 5, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(table[2], 10, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(table[3], 15, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(table[4], 20, index_roe, total_roe, total_finish, spending)    
    rpt.add_table(table, formats)

    rpt.add_string("One Unit (" + rpt.format_ccy(CONST.BUDGET_GROSS) + ") - " + rpt.format_pct(CONST.BUDGET_GROSS / total_roe))
    rpt.add_string("One Million - " + rpt.format_pct(1000000 / total_roe))
    rpt.add_string("Net Worth - " + rpt.format_ccy( total_roe ))
    rpt.add_string("Four Percent - " + rpt.format_ccy( total_finish ))
    rpt.add_string("Since Inception (Beat %11.11) - " + rpt.format_pct( ( ( index_roe / CONST.INCEPT_INDEX ) ** ( 1 / ((datetime.today().date()-CONST.INCEPT_DATE).days / 365.25) ) ) - 1 )
        + " (" + rpt.format_ccy(index_roe) + " / " + rpt.format_ccy(CONST.INCEPT_INDEX) + ", " + rpt.format_ccy(((datetime.today().date()-CONST.INCEPT_DATE).days / 365.25)) + " years)")

def populate_stress_test_twenty_percent_drop(rpt, index_roe, total_roe, total_finish, spending):
    rpt.add_heading("Stress Test - 20% Drop")
    index_roe *= 0.8
    total_roe *= 0.8
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT, rpt.CONST_FORMAT_CCY_INT_COLOR, rpt.CONST_FORMAT_YEARS, rpt.CONST_FORMAT_YEARS, rpt.CONST_FORMAT_DATE_SHORT]
    table = [
        [ "", "%", "Inf", "5mY", "4%Y", "Date" ],
        [ "5" ],
        [ "10" ],
        [ "15" ],
        [ "20" ],
        ]
    append_inflection_report(table[1], 5, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(table[2], 10, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(table[3], 15, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(table[4], 20, index_roe, total_roe, total_finish, spending)    
    rpt.add_table(table, formats)

def populate_stress_test_fifty_percent_drop_from_max(rpt, index_roe_max, index_roe, total_roe, total_finish, spending):
    rpt.add_heading("Stress Test - 50% Drop From Max")
    factor = (index_roe_max * 0.5) / index_roe 
    index_roe *= factor
    total_roe *= factor
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT, rpt.CONST_FORMAT_CCY_INT_COLOR, rpt.CONST_FORMAT_YEARS, rpt.CONST_FORMAT_YEARS, rpt.CONST_FORMAT_DATE_SHORT]
    table = [
        [ "", "%", "Inf", "5mY", "4%Y", "Date" ],
        [ "5" ],
        [ "10" ],
        [ "15" ],
        [ "20" ],
        ]
    append_inflection_report(table[1], 5, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(table[2], 10, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(table[3], 15, index_roe, total_roe, total_finish, spending)    
    append_inflection_report(table[4], 20, index_roe, total_roe, total_finish, spending)    
    rpt.add_table(table, formats)
    rpt.add_string( "Factor " + rpt.format_pct(factor) + " CNW " + rpt.format_ccy(total_roe) )
    
def main():
    log.info("Started...")
   
    rpt = report()
    json_total = _abl.portfolios_history_by_portfolio_id_date(CONST.PORTFOLIO_TOTAL, datetime.today().date())
    json_total_ytd_base = _abl.portfolios_history_by_portfolio_id_date(CONST.PORTFOLIO_TOTAL, _common.get_ytd_base_date())
    total_roe = json_total['value']
    total_finish = float( CONST.BUDGET_GROSS ) / float( CONST.PLAN_FINISH_PCT )
    index_roe = json_total['index']
    index_roe_max = _abl.portfolios_history_max_index_by_portfolio_id(CONST.PORTFOLIO_TOTAL)['index']
    ytd_base_index_roe = json_total_ytd_base['index']
    
    # Determine cash made this year
    profit = _abl.portfolio_returns_by_id(CONST.PORTFOLIO_TOTAL)['profitYearToDate']

    populate_summary(rpt, index_roe, total_roe, total_finish, float( CONST.BUDGET_GROSS ))
    populate_stress_test_twenty_percent_drop(rpt, index_roe, total_roe, total_finish, float( CONST.BUDGET_GROSS ))
    populate_stress_test_fifty_percent_drop_from_max(rpt, index_roe_max, index_roe, total_roe, total_finish, float( CONST.BUDGET_GROSS ))
    
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