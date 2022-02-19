'''
Created on Dec 8, 2019

@author: scanlom
'''

from decimal import Decimal
from requests import get, post, put, delete
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

def ref_data_focus():
    url = 'http://localhost:8081/blue-lion/read/ref-data/focus'
    response = get(url)
    return response.json()

def ref_data_by_symbol( symbol ):
    url = 'http://localhost:8081/blue-lion/read/ref-data?symbol=%s' % (symbol)
    response = get(url)
    if response.status_code == 200:
        return response.json()
    return None

def post_ref_data( symbol, description, sector, industry ):
    url = 'http://localhost:8083/blue-lion/write/ref-data'
    r = post(url, json={'symbol':symbol, 'symbolAlphaVantage':symbol, 'description':description, 'sector':sector, 'industry':industry, 'active':True, 'focus': False} )
    r.raise_for_status()

def put_ref_data( id, symbol, symbolAlphaVantage, description, sector, industry, active, focus ):
    url = 'http://localhost:8083/blue-lion/write/ref-data/%d' % (id)
    r = put(url, json={'id':id, 'symbol':symbol, 'symbolAlphaVantage':symbolAlphaVantage, 'description':description, 'sector':sector, 'industry':industry, 'active':active, 'focus':focus} )
    r.raise_for_status()
    
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

def mdh_by_ref_data_id_date( ref_data_id, date ):
    url = 'http://localhost:8081/blue-lion/read/market-data-historical?refDataId=%d&date=%s' % (ref_data_id, date)
    r = get(url)
    if r.status_code == 200:
        return r.json()
    return None

def post_market_data_historical( date, ref_data_id, close, adj_close ):
    url = 'http://localhost:8083/blue-lion/write/market-data-historical'
    r = post(url, json={'date':date, 'refDataId':ref_data_id, 'close':float(close), 'adjClose':float(adj_close)} )
    r.raise_for_status()

def put_market_data_historical( id, date, ref_data_id, close, adj_close ):
    url = 'http://localhost:8083/blue-lion/write/market-data-historical/%d' % (id)
    r = put(url, json={'id':id, 'date':date, 'refDataId':ref_data_id, 'close':float(close), 'adjClose':float(adj_close)} )
    r.raise_for_status()

def put_portfolio( id, name, value, index, divisor, cash, debt, value_total_capital, index_total_capital, divisor_total_capital ):
    url = 'http://localhost:8083/blue-lion/write/portfolios/%d' % (id)
    r = put(url, json={'id':id, 'name':name, 'value':float(value), 'index':float(index), 'divisor':float(divisor), 'cash':float(cash), 'debt':float(debt), 
    'valueTotalCapital':float(value_total_capital), 'indexTotalCapital':float(index_total_capital), 'divisorTotalCapital':float(divisor_total_capital)} )
    r.raise_for_status()

def positions_by_symbol_portfolio_id( symbol, portfolio_id ):
    url = 'http://localhost:8081/blue-lion/read/positions?symbol=%s&portfolioId=%d' % (symbol, portfolio_id)
    r = get(url)
    if r.status_code == 200:
        return r.json()
    return None

def put_position( data ):
    url = 'http://localhost:8083/blue-lion/write/positions/%d' % (data['id'])
    r = put(url, json=data )
    r.raise_for_status()

def post_position( data ):
    url = 'http://localhost:8083/blue-lion/write/positions'
    r = post(url, json=data )
    r.raise_for_status()

def portfolios_history_by_portfolio_id_date( portfolio_id, date ):
    url = 'http://localhost:8081/blue-lion/read/portfolios-history?portfolioId=%d&date=%s' % (portfolio_id, date)
    r = get(url)
    if r.status_code == 200:
        return r.json()
    return None

def post_portfolios_history( data ):
    url = 'http://localhost:8083/blue-lion/write/portfolios-history'
    r = post(url, json=data )
    r.raise_for_status()

def projections_by_symbol( symbol ):
    url = 'http://localhost:8081/blue-lion/read/enriched-projections?symbol=%s' % (symbol)
    response = get(url)
    if response.status_code == 200:
        return response.json()
    return None

def simfin_income_by_ticker( ticker ):
    url = 'http://localhost:8081/blue-lion/read/simfin-income?ticker=%s' % (ticker)
    r = get(url)
    r.raise_for_status()
    return r.json()

def post_simfin_income( data ):
    url = 'http://localhost:8083/blue-lion/write/simfin-income'
    r = post(url, json=data )
    r.raise_for_status()

def delete_simfin_income_by_id( id ):
    url = 'http://localhost:8083/blue-lion/write/simfin-income/%d' % (id)
    r = delete(url)
    r.raise_for_status()

def simfin_balance_by_ticker( ticker ):
    url = 'http://localhost:8081/blue-lion/read/simfin-balance?ticker=%s' % (ticker)
    r = get(url)
    r.raise_for_status()
    return r.json()

def post_simfin_balance( data ):
    url = 'http://localhost:8083/blue-lion/write/simfin-balance'
    r = post(url, json=data )
    r.raise_for_status()

def delete_simfin_balance_by_id( id ):
    url = 'http://localhost:8083/blue-lion/write/simfin-balance/%d' % (id)
    r = delete(url)
    r.raise_for_status()

def simfin_cashflow_by_ticker( ticker ):
    url = 'http://localhost:8081/blue-lion/read/simfin-cashflow?ticker=%s' % (ticker)
    r = get(url)
    r.raise_for_status()
    return r.json()

def post_simfin_cashflow( data ):
    url = 'http://localhost:8083/blue-lion/write/simfin-cashflow'
    r = post(url, json=data )
    r.raise_for_status()

def delete_simfin_cashflow_by_id( id ):
    url = 'http://localhost:8083/blue-lion/write/simfin-cashflow/%d' % (id)
    r = delete(url)
    r.raise_for_status()
    
def main():
    log.info("Started...")
    
    # Test
    print(cagr(5, 5.10, 0.40, 0.10, 18, 183.43))
    # post_simfin_income({'date':'2019-12-13', 'ticker':'Mikey'})
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)