'''
Created on Apr 7, 2021
@author: scanlom
'''

from datetime import date
from decimal import Decimal

class CONST:
    FIVE_MILLION      = Decimal(5000000)
    DAYS_IN_YEAR      = 365

    BUDGET_BASE       = Decimal(80000)
    BUDGET_RENT       = Decimal(10000)
    BUDGET_CAR        = Decimal(3000)
    BUDGET_BLR        = Decimal(0)
    BUDGET_TRAVEL     = Decimal(10000)
    BUDGET_HELPER     = Decimal(0)
    BUDGET_MONCHICHI  = Decimal(7000)
    BUDGET_DEUX       = Decimal(6000)
    BUDGET_FUMI       = Decimal(5000)
    BUDGET_MIKE       = Decimal(5000)
    BUDGET_MEDICAL    = Decimal(1000)
    BUDGET_SPECIAL    = Decimal(0)

    BUDGET_SPENDING   = BUDGET_BASE + BUDGET_RENT + BUDGET_CAR + BUDGET_TRAVEL + BUDGET_HELPER + BUDGET_MONCHICHI + BUDGET_DEUX + BUDGET_FUMI + BUDGET_MIKE + BUDGET_MEDICAL + BUDGET_SPECIAL
    BUDGET_TAX_RATE   = Decimal(0.1823)     # 2021/04/02 - Cap Gains plus Obamacare
    BUDGET_GROSS      = float(round((BUDGET_SPENDING)/(1-BUDGET_TAX_RATE),0))
    
    PLAN_FINISH_PCT   = 0.04
    
    INCEPT_INDEX   = 72444.29
    INCEPT_DATE    = date(2021,4,19)
    
    MAX_MARKET_DATA_CALLS = 500

    PORTFOLIO_TOTAL = 1
    PORTFOLIO_SELFIE = 2
    PORTFOLIO_OAK = 3
    PORTFOLIO_MANAGED = 4
    PORTFOLIO_RISK_ARB = 5
    PORTFOLIO_TRADE_FIN = 6
    PORTFOLIO_QUICK = 7
    PORTFOLIO_PORTFOLIO = 8
    PORTFOLIO_NONE = 99