'''
Created on Jul 20, 2013

@author: scanlom
'''

from datetime import datetime
import math
from api_database import database2
from api_log import log
from api_mail import send_mail_html_self
from api_reporting import report
import api_blue_lion as _abl

def check_index_and_total(db, t_total, t_index, k_portfolio, msg, table):
    t_total = db.get_balance(t_total)
    t_index = db.get_index_history(t_index, datetime.today().date())
    k_total_row = _abl.portfolio_by_id(k_portfolio)
    table.append([ msg + " Value", t_total, k_total_row['value'] ])
    table.append([ msg + " Index", t_index, k_total_row['index'] ])
    if math.isclose(t_total, k_total_row['value'],abs_tol=0.01) and math.isclose(t_index, k_total_row['index'],abs_tol=0.01):
        return True
    return False

def main():
    log.info("Started...")
   
    db = database2()
    rpt = report()
    status = "GREEN"

    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_NONE ]
    table = [
        [ "Category", "Togabou", "Kapparu" ],
        ]

    if not check_index_and_total(db, db.CONST_BALANCES_TYPE_TOTAL_ROE, db.CONST_INDEX_ROE, db.CONST_BLB_PORTFOLIO_TOTAL, "Total", table):
        status = "RED"
    if not check_index_and_total(db, db.CONST_BALANCES_TYPE_TOTAL_PLAY, db.CONST_INDEX_PLAY, db.CONST_BLB_PORTFOLIO_SELFIE, "Selfie", table):
        status = "RED"
    if not check_index_and_total(db, db.CONST_INDEX_OAK, db.CONST_INDEX_OAK, db.CONST_BLB_PORTFOLIO_OAK, "Oak", table):
        status = "RED"
    if not check_index_and_total(db, db.CONST_BALANCES_TYPE_TOTAL_MANAGED, db.CONST_INDEX_MANAGED, db.CONST_BLB_PORTFOLIO_MANAGED, "Managed", table):
        status = "RED"
    if not check_index_and_total(db, db.CONST_INDEX_RISK_ARB, db.CONST_INDEX_RISK_ARB, db.CONST_BLB_PORTFOLIO_RISK_ARB, "Risk Arb", table):
        status = "RED"
    if not check_index_and_total(db, db.CONST_INDEX_TRADE_FIN, db.CONST_INDEX_TRADE_FIN, db.CONST_BLB_PORTFOLIO_TRADE_FIN, "Trade Fin", table):
        status = "RED"
    if not check_index_and_total(db, db.CONST_INDEX_QUICK, db.CONST_INDEX_QUICK, db.CONST_BLB_PORTFOLIO_QUICK, "Quick", table):
        status = "RED"

    t_total = db.get_balance(db.CONST_BALANCES_TYPE_TOTAL_ROTC)
    t_index = db.get_index_history(db.CONST_INDEX_ROTC, datetime.today().date())
    k_total_row = _abl.portfolio_by_id(db.CONST_BLB_PORTFOLIO_TOTAL)
    table.append([ "ROTC Value", t_total, k_total_row['valueTotalCapital'] ])
    table.append([ "ROTC Index", t_index, k_total_row['indexTotalCapital'] ])
    if not  (math.isclose(t_total, k_total_row['valueTotalCapital'],abs_tol=0.01) and math.isclose(t_index, k_total_row['indexTotalCapital'],abs_tol=0.01)):
        status = "RED"

    rpt.add_table(table, formats)

    # Send a summary mail
    subject = "BLB Recon - " + status
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")