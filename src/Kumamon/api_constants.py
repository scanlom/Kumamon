'''
Created on Apr 7, 2021

@author: scanlom
'''

from datetime import date
from decimal import Decimal

class CONST:
    FIVE_MILLION      = Decimal(5000000)

    BUDGET_BASE       = Decimal(66000)
    BUDGET_RENT       = Decimal(12000)
    BUDGET_CAR        = Decimal(2000)
    BUDGET_TRAVEL     = Decimal(10000)
    BUDGET_HELPER     = Decimal(0)
    BUDGET_MONCHICHI  = Decimal(6000)
    BUDGET_DEUX       = Decimal(6000)
    BUDGET_FUMI       = Decimal(5000)
    BUDGET_MIKE       = Decimal(5000)
    BUDGET_MEDICAL    = Decimal(10000)
    BUDGET_SPECIAL    = Decimal(0)

    BUDGET_SPENDING   = BUDGET_BASE + BUDGET_RENT + BUDGET_CAR + BUDGET_TRAVEL + BUDGET_HELPER + BUDGET_MONCHICHI + BUDGET_DEUX + BUDGET_FUMI + BUDGET_MIKE + BUDGET_MEDICAL + BUDGET_SPECIAL
    BUDGET_TAX_RATE   = Decimal(0.1823)     # 2021/04/02 - Cap Gains plus Obamacare
    BUDGET_GROSS      = Decimal(round((BUDGET_SPENDING)/(1-BUDGET_TAX_RATE),0))
    
    PLAN_FINISH_PCT   = Decimal(0.04)
    
    INCEPT_INDEX   = Decimal(72444.29)
    INCEPT_DATE    = date(2021,4,19)
    
    MAX_MARKET_DATA_CALLS = 500