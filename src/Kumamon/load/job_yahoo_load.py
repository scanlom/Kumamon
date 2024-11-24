'''
Created on Nov 18, 2024
@author: scanlom
'''

from yahooquery import Ticker
from lib_log import log
from interface_financials import financials_by_ticker
import api_blue_lion as _abl

def load_statements( ticker, statements, get_statements, post_statement, delete_statement ):
    entries = get_statements(ticker)
    for foo in statements:
        log.info("Processing %s" % foo['reportDate'])
        skip = False
        for e in entries:
            if e['fiscalYear'] == foo['fiscalYear']:
                log.info("Collision found, type %s" % (e['entryType']))
                if 'S' == e['entryType']:
                    log.info("Skipping") # SimFin takes higher priority
                    skip = True
                elif 'O' == e['entryType']: # Overloaded takes higher priority
                    log.info("Skipping")
                    skip = True
                else: # Overwrite Manual or other Yahoo records
                    log.info("Overwriting, entryType " + e['entryType'])
                    delete_statement(e['id'])
        
        if not skip:
            log.info("Inserting")
            post_statement(foo)

def main():
    log.info("Started...")

    tickers = [
        '1373.HK',
        # 'BATS.L',
        # 'U11.SI',
        # 'BOL.PA',
        # '8074.T',
        # 'NESN.SW',
        # 'MRO.L',
        # 'HEIO.AS',
        # 'ULVR.L',
        # 'UMG.AS',
        # 'DHL.DE',
    ]

    for ticker in tickers:
        try:
            json_income_statements, json_balance_sheets, json_cash_flow = financials_by_ticker(ticker)
            load_statements( ticker, json_income_statements, _abl.simfin_income_by_ticker, _abl.post_simfin_income, _abl.delete_simfin_income_by_id)
            load_statements( ticker, json_balance_sheets, _abl.simfin_balance_by_ticker, _abl.post_simfin_balance, _abl.delete_simfin_balance_by_id)
            load_statements( ticker, json_cash_flow, _abl.simfin_cashflow_by_ticker, _abl.post_simfin_cashflow, _abl.delete_simfin_cashflow_by_id)
        except Exception as err:
            # If we can't retrieve financials for one symbol, continue for now
            log.warning( "Unable to process financials for %s" % ( ticker ))
            continue

    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 