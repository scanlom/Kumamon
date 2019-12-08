'''
Created on Dec 8, 2019

@author: scanlom
'''

from decimal import Decimal

CONST_DIV_GROWTH    = Decimal(0.0981)

def cagr( years, eps, payout, growth, pe_terminal, price ):
    div_bucket = Decimal(0.0)
    for i in range (1,years+1):
        div_bucket = div_bucket * (Decimal(1) + CONST_DIV_GROWTH)
        div_bucket = div_bucket + (eps * payout)
        eps = eps * (Decimal(1) + growth)
    return ((((eps * pe_terminal) + div_bucket) / price) ** (Decimal(1.0) / years)) - Decimal(1)