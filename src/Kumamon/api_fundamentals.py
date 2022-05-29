'''
Created on Feb 6, 2022

@author: scanlom
'''

import json as _json
import re as _re
import requests as _requests
from api_log import log

CONST_URL_QUOTE = 'https://finance.yahoo.com/quote'
CONST_FORMAT_URL_HISTORICALS = 'https://finance.yahoo.com/quote/{}/history?period1=0&period2=9999999999&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true'
CONST_HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
CONST_TIMEOUT = 10

def get_json( url ):
    html = _requests.get(url=url, headers=CONST_HEADERS, timeout=CONST_TIMEOUT).text
    json_str = html.split('root.App.main =')[1].split(
        '(this)')[0].split(';\n}')[0].strip()
    data = _json.loads(json_str)[
        'context']['dispatcher']['stores']
    # return data
    data = _json.dumps(data).replace('{}', 'null')
    data = _re.sub(
        r'\{[\'|\"]raw[\'|\"]:(.*?),(.*?)\}', r'\1', data)

    return _json.loads(data)

def get_quote( ticker ):
    return get_json( "{}/{}".format(CONST_URL_QUOTE, ticker ) )

def get_financials( ticker ):
    return get_json( "{}/{}/financials".format(CONST_URL_QUOTE, ticker ) )

def get_historicals( ticker ):
    return get_json( CONST_FORMAT_URL_HISTORICALS.format( ticker ) )

def main():
    log.info("Started...")
    
    ticker = "MSFT"
    historicals = get_historicals( ticker )
    print( historicals['HistoricalPriceStore']['prices'][0] )

    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)