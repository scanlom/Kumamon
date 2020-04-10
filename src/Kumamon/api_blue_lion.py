'''
Created on Dec 8, 2019

@author: scanlom
'''

from decimal import Decimal
from requests import get, post, put
from api_log import log

def confidence( research ):
    # MSTODO - Desperately need to move this to post
    url = 'http://localhost:8080/blue-lion/utils/confidence?research=%s' % ("".join(research.split()).replace('%','').replace('.','').replace('/','').
                                                                            replace(";","").replace("&",""))
    response = get(url)
    return response.json()['confidence']

def cagr( years, eps, payout, growth, pe_terminal, price ):
    url = 'http://localhost:8080/blue-lion/utils/cagr?years=%f&eps=%f&payout=%f&growth=%f&peterminal=%f&price=%f' % (years, eps, payout, growth, pe_terminal, price)
    response = get(url)
    return response.json()['cagr']

def last( symbol ):
    url = 'http://localhost:8081/blue-lion/read/market-data?symbol=%s' % (symbol)
    response = get(url)
    return Decimal(response.json()['last'])

def ref_data():
    url = 'http://localhost:8081/blue-lion/read/ref-data'
    response = get(url)
    return response.json()
    
def market_data_by_symbol( symbol ):
    url = 'http://localhost:8081/blue-lion/read/market-data?symbol=%s' % (symbol)
    response = get(url)
    if response.status_code == 200:
        return response.json()
    return None

def post_market_data( ref_data_id, last ):
    url = 'http://localhost:8083/blue-lion/write/market-data'
    r = post(url, json={'refDataId':ref_data_id, 'last':float(last)} )
    r.raise_for_status()

def put_market_data( id, ref_data_id, last ):
    url = 'http://localhost:8083/blue-lion/write/market-data/%d' % (id)
    r = put(url, json={'id':id, 'refDataId':ref_data_id, 'last':float(last)} )
    r.raise_for_status()

def post_simfin_income( data ):
    url = 'http://localhost:8083/blue-lion/write/simfin-income'
    r = post(url, json=data )
    r.raise_for_status()

    
def main():
    log.info("Started...")
    
    # Test
    # print(cagr(5, 2.16, 0, 0.15, 15, 41.61))
    post_simfin_income()
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)