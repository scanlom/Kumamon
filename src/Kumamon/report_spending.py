'''
Created on Jul 14, 2013

@author: scanlom
'''

from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from time import localtime
from time import strftime
from api_constants import CONST
from api_database import database2
from api_log import log
from api_mail import send_mail_html_self
from api_reporting import report

def append_budget_row( db, table, name, types, budget ):
    day_of_year = datetime.now().timetuple().tm_yday
    if day_of_year == 1:
        day_of_year = 365 # Special Jan 1 handling
    spending = db.get_ytd_spending_sum_by_types( types )
    projected = spending * 365 / day_of_year
    table.append( [ name, spending, projected, budget, budget - projected ] )

def calculate_fumi_projected( table, base_row, fumi_row, tracking_col ):
    # Fumi's projected payout is 0.5 of base tracking if positive, plus what is left of her allocation if positive
    projected = Decimal( 0.0 )
    if table[base_row][tracking_col] > 0:
        projected += table[base_row][tracking_col] * Decimal( 0.5 )
    if table[fumi_row][tracking_col] > 0:
        projected += table[fumi_row][tracking_col]
    return projected

def calculate_recon_projected( table, standard_rows, base_row, fumi_row, projected_col, tracking_col ):
    # Add back in Fumi's projected payout 
    projected = table[base_row][projected_col]
    projected += table[fumi_row][projected_col]
    projected += calculate_fumi_projected( table, base_row, fumi_row, tracking_col )
    for row in standard_rows:
        projected += table[row][projected_col]
    return projected

def main():
    log.info("Started...")
    db = database2()
    rpt = report()
    
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY_COLOR]
    table = [
        [ "Category", "Spent", "Projected", "Budget", "Tracking" ],
        ]
    append_budget_row( db, table, "Base", [0,2,3,4,5,8,12,96], CONST.BUDGET_BASE )
    append_budget_row( db, table, "Rent", [1], CONST.BUDGET_RENT )
    append_budget_row( db, table, "Travel", [7], CONST.BUDGET_TRAVEL )
    append_budget_row( db, table, "Helper", [9], CONST.BUDGET_HELPER )
    append_budget_row( db, table, "Monchichi", [94], CONST.BUDGET_MONCHICHI )
    append_budget_row( db, table, "Deux", [93], CONST.BUDGET_DEUX )
    append_budget_row( db, table, "Fumi", [11], CONST.BUDGET_FUMI )
    append_budget_row( db, table, "Mike", [6,10], CONST.BUDGET_MIKE )
    append_budget_row( db, table, "Special", [95,97,98,99], CONST.BUDGET_SPECIAL )
    append_budget_row( db, table, "Total", [0,1,2,3,4,5,6,7,8,9,10,11,12,93,94,95,96,97,98,99], CONST.BUDGET_SPENDING )
    recon_projected = calculate_recon_projected( table, [2,3,4,5,6,8,9], 1, 7, 2, 4 )
    table.append( [ "Recon", db.get_ytd_spending_sum(), recon_projected, CONST.BUDGET_SPENDING, CONST.BUDGET_SPENDING - recon_projected ] )
    fumi_projected = calculate_fumi_projected( table, 1, 7, 4 )
    table.append( [ "Payout", 0, fumi_projected, 0, 0 ] )
    
    rpt.add_heading("Summary")
    rpt.add_table(table, formats)
    
    plan_projected = (recon_projected + CONST.BUDGET_FIXED) / (1 - CONST.BUDGET_TAX_RATE)
    rpt.add_string( "BLRP " + rpt.format_ccy(plan_projected) + "=(" +
                    rpt.format_ccy(recon_projected) + "+" +
                    rpt.format_ccy(CONST.BUDGET_FIXED) +
                    ")/(1-" + rpt.format_ccy(CONST.BUDGET_TAX_RATE) + ")"
                    )
    rpt.add_string( "BLRB " + rpt.format_ccy(CONST.BUDGET_GROSS) + "=(" +
                    rpt.format_ccy(CONST.BUDGET_SPENDING) + "+" +
                    rpt.format_ccy(CONST.BUDGET_FIXED) +
                    ")/(1-" + rpt.format_ccy(CONST.BUDGET_TAX_RATE) + ")"     
                    )

    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_NONE]
    table = [
        [ "Date", "Amount", "Description" ],
        ]    
    rows = db.get_ytd_spendings_by_types([0,2,3,4,5,8,12,96],250)
    for row in rows:
        table.append([row.date, row.amount, row.description])
    rpt.add_heading("Base - 250 Plus")
    rpt.add_table(table, formats)
    
    subject = 'Blue Tree - ' + rpt.format_ccy(plan_projected) + ' / ' + rpt.format_ccy(CONST.BUDGET_GROSS)
     
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")