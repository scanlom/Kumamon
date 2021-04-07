'''
Created on Apr 7, 2021

@author: scanlom
'''

from datetime import date
from decimal import Decimal

class CONST:
    FIVE_MILLION      = Decimal(5000000)

    BUDGET_BASE       = Decimal(75000)
    BUDGET_RENT       = Decimal(73000)
    BUDGET_TRAVEL     = Decimal(10000)
    BUDGET_HELPER     = Decimal(12000)
    BUDGET_MONCHICHI  = Decimal(12000)
    BUDGET_DEUX       = Decimal(12000)
    BUDGET_FUMI       = Decimal(5000)
    BUDGET_MIKE       = Decimal(5000)
    BUDGET_SPECIAL    = Decimal(0)

    BUDGET_SPENDING   = BUDGET_BASE + BUDGET_RENT + BUDGET_TRAVEL + BUDGET_HELPER + BUDGET_MONCHICHI + BUDGET_DEUX + BUDGET_FUMI + BUDGET_MIKE + BUDGET_SPECIAL
    BUDGET_FIXED      = Decimal(10000)      # 2021/04/02 - AIA Plans
    BUDGET_TAX_RATE   = Decimal(0.1823)     # 2021/04/02 - Cap Gains plus Obamacare
    BUDGET_GROSS      = Decimal(round((BUDGET_SPENDING+BUDGET_FIXED)/(1-BUDGET_TAX_RATE),0))
    BUDGET_SAVINGS    = Decimal(94000)      # 2021/04/08 - (PATC 373k + ORSO 25k) * 75% - Spending 204k)

    PLAN_FINISH_PCT                 = Decimal(0.04)
    PLAN_RETIRE_DATE_LATE           = date(2035,4,17)   # Definite retirement at 58
    PLAN_RETIRE_DATE_EARLY          = date(2024,3,1)    # Hoped retirement five years at JPMC