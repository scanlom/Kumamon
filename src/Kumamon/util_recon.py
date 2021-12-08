'''
Created on May 15, 2019

@author: scanlom
'''

from datetime import datetime
from datetime import timedelta
from api_database import database2
from api_log import log

def main():
    log.info("Started...")
    db = database2()
    date = datetime.now().date()
    recon = 1
    log.info("%s %s\t%s\t\t%s\t%s\t%s\t%s\t%s" % (date, "recon", "pos_gs", "pos_gs_ira", "pos_owe_p", "neg_cash_total", "neg_cash_s", "neg_cash_m"))
    while recon != 0:
        pos_gs = db.get_balance_history(db.CONST_BALANCES_TYPE_GS, date)
        pos_gs_ira = db.get_balance_history(db.CONST_BALANCES_TYPE_GS_IRA, date)
        pos_owe_portfolio = db.get_balance_history(db.CONST_BALANCES_TYPE_OWE_PORTFOLIO, date)
        neg_cash_total = db.get_portfolio_history(db.CONST_PORTFOLIO_CASH, db.CONST_SYMBOL_CASH, date)
        neg_cash_self = db.get_portfolio_history(db.CONST_PORTFOLIO_SELF, db.CONST_SYMBOL_CASH, date)
        neg_cash_managed = db.get_portfolio_history(db.CONST_PORTFOLIO_MANAGED, db.CONST_SYMBOL_CASH, date)
        recon = (pos_gs + pos_gs_ira + pos_owe_portfolio) - (neg_cash_total + neg_cash_self + neg_cash_managed)
        log.info("%s %s\t%s\t%s\t\t%s\t%s\t\t%s\t%s" % (date, recon, pos_gs, pos_gs_ira, pos_owe_portfolio, 
                                                    neg_cash_total, neg_cash_self, neg_cash_managed))
        date -= timedelta(1)    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 