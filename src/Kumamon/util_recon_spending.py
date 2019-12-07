'''
Created on May 15, 2019

@author: scanlom
'''

from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from api_database import database2
from api_log import log

CONST_BUDGET_UNIT      = Decimal(13166.66)

def main():
    log.info("Started...")
    db = database2()
    d = date(2019,11,27)

    pos_hsbc = db.get_balance_history(db.CONST_BALANCES_TYPE_HSBC, d)
    pos_vb = db.get_balance_history(db.CONST_BALANCES_TYPE_VIRTUAL_BANK, d)
    pos_jpy = db.get_balance_history(db.CONST_BALANCES_TYPE_JPY, d)
    neg_owe_portfolio = db.get_balance_history(db.CONST_BALANCES_TYPE_OWE_PORTFOLIO, d)
    neg_amex_cx = db.get_balance_history(db.CONST_BALANCES_TYPE_AMEX_CX, d)
    neg_capital_one = db.get_balance_history(db.CONST_BALANCES_TYPE_CAPITAL_ONE, d)
    neg_hsbc_visa = db.get_balance_history(db.CONST_BALANCES_TYPE_HSBC_VISA, d)
    budget_recon = (pos_hsbc + pos_vb + pos_jpy) - (neg_owe_portfolio + neg_amex_cx + neg_capital_one + neg_hsbc_visa)

    paid = db.get_balance_history(db.CONST_BALANCES_TYPE_PAID, d)
    tax = db.get_balance_history(db.CONST_BALANCES_TYPE_TAX, d)
    savings = db.get_balance_history(db.CONST_BALANCES_TYPE_SAVINGS, d)
    spending = paid - tax - savings - (budget_recon - CONST_BUDGET_UNIT)

    recon = spending - db.get_ytd_spending_sum_by_date(d)

    log.info(recon)
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 