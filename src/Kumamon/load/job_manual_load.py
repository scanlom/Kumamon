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
FILE_BALANCE_SHEET = "~/python/Kumamon/src/Kumamon/template/balance_sheet.csv"
FILE_CASH_FLOW = "~/python/Kumamon/src/Kumamon/template/cash_flow.csv"

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

def load_file( path ):
    log.info("Loading file from " + path)

    df = _p.read_csv(path, skiprows=1)
    df = df.mul([1,1,1,1]+[MULTIPLIER]*(df.shape[1]-4)) # Multiply all but the first four columns (which are text and date) by the multiplier
    json_statements = loads(df.reset_index().to_json(orient='records',double_precision=0,date_format='iso'))
    for j in json_statements:
        j['publishDate'] = j['restatedDate'] = j['reportDate']
        j['fiscalYear'] = int( j['reportDate'][:4] )
    return json_statements

def main():
    log.info("Started...")

    try:
        load_statements( load_file( FILE_INCOME_STATEMENT ), _abl.simfin_income_by_ticker, _abl.post_simfin_income, _abl.delete_simfin_income_by_id)
        load_statements( load_file( FILE_BALANCE_SHEET ), _abl.simfin_balance_by_ticker, _abl.post_simfin_balance, _abl.delete_simfin_balance_by_id)
        load_statements( load_file( FILE_CASH_FLOW ), _abl.simfin_cashflow_by_ticker, _abl.post_simfin_cashflow, _abl.delete_simfin_cashflow_by_id)
    except Exception as err:
        log.exception(err)
        
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 