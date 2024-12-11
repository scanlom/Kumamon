'''
Created on Nov 18, 2024
@author: scanlom
'''

import pandas as _p
from json import loads
from lib_log import log
import api_blue_lion as _abl

MULTIPLIER = 1000000
FILE_INCOME_STATEMENT = "~/python/Kumamon/src/Kumamon/template/income_statement.csv"

def load_statements( statements, get_statements, post_statement, delete_statement ):
    tickers_to_entries = {}
    for j in statements:
        log.info("Processing %s, %d" % (j['ticker'],j['fiscalYear']))
        if j['ticker'] not in tickers_to_entries:
            log.info("Getting existing entries...")
            tickers_to_entries[j['ticker']] = get_statements(j['ticker'])
        
        for e in tickers_to_entries[j['ticker']]:
            if e['fiscalYear'] == j['fiscalYear']:
                log.info("Collision found, type %s" % (e['entryType']))
                log.info("Overwriting")
                delete_statement(e['id'])
                break
        
        log.info("Inserting")
        post_statement(j)

def main():
    log.info("Started...")
    log.info("Loading income statements from " + FILE_INCOME_STATEMENT)

    df = _p.read_csv(FILE_INCOME_STATEMENT, skiprows=1)
    df = df.mul([1,1,1,1]+[MULTIPLIER]*(df.shape[1]-4))
    json_income_statements = loads(df.reset_index().to_json(orient='records',double_precision=0,date_format='iso'))
    for j in json_income_statements:
        j['publishDate'] = j['restatedDate'] = j['reportDate']
        j['fiscalYear'] = int( j['reportDate'][:4] )

    try:
        load_statements( json_income_statements, _abl.simfin_income_by_ticker, _abl.post_simfin_income, _abl.delete_simfin_income_by_id)
        # load_statements( ticker, json_balance_sheets, _abl.simfin_balance_by_ticker, _abl.post_simfin_balance, _abl.delete_simfin_balance_by_id)
        # load_statements( ticker, json_cash_flow, _abl.simfin_cashflow_by_ticker, _abl.post_simfin_cashflow, _abl.delete_simfin_cashflow_by_id)
    except Exception as err:
        log.exception(err)
        
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 