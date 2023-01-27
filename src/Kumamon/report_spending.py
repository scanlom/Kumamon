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

CONST_PROJECT_TYPE_PROJECT         = 0
CONST_PROJECT_TYPE_FIXED           = 1

def table_col_sum(table, start, col):
    sum = 0
    for i in range(start, len(table)):
        sum += table[i][col]
    return sum

def append_budget_row( db, table, name, types, budget, project_type ):
    day_of_year = datetime.now().timetuple().tm_yday
    if day_of_year == 1:
        day_of_year = 365 # Special Jan 1 handling
    spending = db.get_ytd_spending_sum_by_types( types )
    if project_type is CONST_PROJECT_TYPE_PROJECT:
        projected = spending * 365 / day_of_year
    elif project_type is CONST_PROJECT_TYPE_FIXED:
        projected = budget if spending < budget else spending
    table.append( [ name, spending, projected, budget, budget - projected ] )

def calculate_fumi_projected( table, base_row, fumi_row, tracking_col ):
    # Fumi's projected payout is 0.5 of base tracking if positive, plus what is left of her allocation if positive
    projected = Decimal( 0.0 )
    if table[base_row][tracking_col] > 0:
        projected += table[base_row][tracking_col] * Decimal( 0.5 )
    if table[fumi_row][tracking_col] > 0:
        projected += table[fumi_row][tracking_col]
    return projected

def main():
    log.info("Started...")
    db = database2()
    rpt = report()
    
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY_COLOR]
    table = [
        [ "Category", "Spent", "Projected", "Budget", "Tracking" ],
        ]
    append_budget_row( db, table, "Base", [0,2,3,4,5,8,12,96], CONST.BUDGET_BASE, CONST_PROJECT_TYPE_PROJECT )
    append_budget_row( db, table, "Rent", [1], CONST.BUDGET_RENT, CONST_PROJECT_TYPE_FIXED )
    append_budget_row( db, table, "Travel", [7], CONST.BUDGET_TRAVEL, CONST_PROJECT_TYPE_FIXED )
    append_budget_row( db, table, "Helper", [9], CONST.BUDGET_HELPER, CONST_PROJECT_TYPE_PROJECT )
    append_budget_row( db, table, "Monchichi", [94], CONST.BUDGET_MONCHICHI, CONST_PROJECT_TYPE_FIXED )
    append_budget_row( db, table, "Deux", [93], CONST.BUDGET_DEUX, CONST_PROJECT_TYPE_FIXED )
    append_budget_row( db, table, "Fumi", [11], CONST.BUDGET_FUMI, CONST_PROJECT_TYPE_FIXED )
    append_budget_row( db, table, "Mike", [6,10], CONST.BUDGET_MIKE, CONST_PROJECT_TYPE_FIXED )
    append_budget_row( db, table, "Medical", [13], CONST.BUDGET_MEDICAL, CONST_PROJECT_TYPE_PROJECT )
    append_budget_row( db, table, "Car", [14], CONST.BUDGET_CAR, CONST_PROJECT_TYPE_PROJECT )
    append_budget_row( db, table, "Special", [92,95,97,98,99], CONST.BUDGET_SPECIAL, CONST_PROJECT_TYPE_PROJECT )
    
    # Append a sub total row. Use the totals from above so we can take advantage of the project types
    table.append( [ "SubTotal", table_col_sum(table, 1, 1), table_col_sum(table, 1, 2), table_col_sum(table, 1, 3), table_col_sum(table, 1, 4) ] )
    
    # Append a row for Fumi's payout. 0.5 of base tracking if positive, plus what is left of her allocation if positive
    fumi_projected = calculate_fumi_projected( table, 1, 7, 4 )
    table.append( [ "Payout", 0, fumi_projected, 0, 0 ] )
    
    # Append a total row 
    subtotal_row = len(table)-2
    payout_row = len(table)-1
    total_projected = table[subtotal_row][2] + table[payout_row][2]
    table.append( [ "Total", table[subtotal_row][1], total_projected, CONST.BUDGET_SPENDING, CONST.BUDGET_SPENDING - total_projected ] )
    
    rpt.add_heading("Summary")
    rpt.add_table(table, formats)
    
    plan_projected = (total_projected) / (1 - CONST.BUDGET_TAX_RATE)
    rpt.add_string( "BLRP " + rpt.format_ccy(plan_projected) + "=(" +
                    rpt.format_ccy(total_projected) +
                    ")/(1-" + rpt.format_ccy(CONST.BUDGET_TAX_RATE) + ")"
                    )
    rpt.add_string( "BLRB " + rpt.format_ccy(CONST.BUDGET_GROSS) + "=(" +
                    rpt.format_ccy(CONST.BUDGET_SPENDING) +
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