'''
Created on Dec 8, 2019
@author: scanlom
'''

from decimal import Decimal
from requests import get, post, put, delete
from lib_log import log

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

def ref_data_positions():
    url = 'http://localhost:8081/blue-lion/read/ref-data/positions'
    response = get(url)
    return response.json()

def ref_data_by_symbol( symbol ):
    url = 'http://localhost:8081/blue-lion/read/ref-data?symbol=%s' % (symbol)
    response = get(url)
    if response.status_code == 200:
        return response.json()
    return None

def run_job_valuation_cut():
    url = 'http://localhost:8085/blue-lion/run/job-valuation-cut'
    r = get(url)
    r.raise_for_status()
    return r.status_code

def execute_book_transaction( data ):
    url = 'http://localhost:8085/blue-lion/run/execute-book-transaction'
    r = post(url, json=data )
    r.raise_for_status()

def post_ref_data( symbol, description, sector, industry ):
    url = 'http://localhost:8083/blue-lion/write/ref-data'
    r = post(url, json={'symbol':symbol, 'symbolAlphaVantage':symbol, 'description':description, 'sector':sector, 'industry':industry, 'active':True } )
    r.raise_for_status()

def put_ref_data( id, symbol, symbolAlphaVantage, description, sector, industry, active ):
    url = 'http://localhost:8083/blue-lion/write/ref-data/%d' % (id)
    r = put(url, json={'id':id, 'symbol':symbol, 'symbolAlphaVantage':symbolAlphaVantage, 'description':description, 'sector':sector, 'industry':industry, 'active':active } )
    r.raise_for_status()
    
def market_data_by_symbol( symbol ):
    url = 'http://localhost:8081/blue-lion/read/market-data?symbol=%s' % (symbol)
    response = get(url)
    if response.status_code == 200:
        return response.json()
    return None

def enriched_market_data_by_symbol( symbol ):
    url = 'http://localhost:8081/blue-lion/read/enriched-market-data?symbol=%s' % (symbol)
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

def portfolios():
    url = 'http://localhost:8081/blue-lion/read/portfolios'
    response = get(url)
    if response.status_code == 200:
        return response.json()
    return None

def portfolio_by_id( id ):
    url = 'http://localhost:8081/blue-lion/read/portfolios/%d' % (id)
    response = get(url)
    if response.status_code == 200:
        return response.json()
    return None

def put_portfolio( data ):
    url = 'http://localhost:8083/blue-lion/write/portfolios/%d' % (data['id'])
    r = put(url, json=data )
    r.raise_for_status()

def positions_by_symbol_portfolio_id( symbol, portfolio_id ):
    url = 'http://localhost:8081/blue-lion/read/positions?symbol=%s&portfolioId=%d' % (symbol, portfolio_id)
    r = get(url)
    if r.status_code == 200:
        return r.json()
    return None

def position_by_id( id ):
    url = 'http://localhost:8081/blue-lion/read/positions/%d' % (id)
    r = get(url)
    if r.status_code == 200:
        return r.json()
    return None

def enriched_positions_by_portfolio_id( portfolio_id ):
    url = 'http://localhost:8081/blue-lion/read/enriched-positions?portfolioId=%d' % (portfolio_id)
    r = get(url)
    if r.status_code == 200:
        return r.json()
    return None

def enriched_positions_all_by_portfolio_id( portfolio_id ):
    url = 'http://localhost:8081/blue-lion/read/enriched-positions-all?portfolioId=%d' % (portfolio_id)
    r = get(url)
    if r.status_code == 200:
        return r.json()
    return None

def put_position( data ):
    url = 'http://localhost:8083/blue-lion/write/positions/%d' % (data['id'])
    r = put(url, json=data )
    r.raise_for_status()

def put_positions_history( data ):
    url = 'http://localhost:8083/blue-lion/write/positions-history/%d' % (data['id'])
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

def portfolios_history_by_date( date ):
    url = 'http://localhost:8081/blue-lion/read/portfolios-history?date=%s' % (date)
    r = get(url)
    if r.status_code == 200:
        return r.json()
    return None

def positions_history_by_portfolio_id_date( portfolio_id, date ):
    url = 'http://localhost:8081/blue-lion/read/positions-history?portfolioId=%d&date=%s' % (portfolio_id, date)
    r = get(url)
    if r.status_code == 200:
        return r.json()
    return None

def enriched_positions_history_by_portfolio_id_date( portfolio_id, date ):
    url = 'http://localhost:8081/blue-lion/read/enriched-positions-history?portfolioId=%d&date=%s' % (portfolio_id, date)
    r = get(url)
    if r.status_code == 200:
        return r.json()
    return None

def portfolio_returns_by_id( id ):
    url = 'http://localhost:8081/blue-lion/read/portfolio-returns/%d' % (id)
    r = get(url)
    if r.status_code == 200:
        return r.json()
    return None

def position_returns_by_id( id ):
    url = 'http://localhost:8081/blue-lion/read/position-returns/%d' % (id)
    r = get(url)
    if r.status_code == 200:
        return r.json()
    return None

def portfolios_history_max_index_by_portfolio_id( portfolio_id ):
    url = 'http://localhost:8081/blue-lion/read/portfolios-history-max-index?portfolioId=%d' % (portfolio_id)
    r = get(url)
    if r.status_code == 200:
        return r.json()
    return None

def post_portfolios_history( data ):
    url = 'http://localhost:8083/blue-lion/write/portfolios-history'
    r = post(url, json=data )
    r.raise_for_status()

def put_portfolios_history( data ):
    url = 'http://localhost:8083/blue-lion/write/portfolios-history/%d' % (data['id'])
    r = put(url, json=data )
    r.raise_for_status()

def post_positions_history( data ):
    url = 'http://localhost:8083/blue-lion/write/positions-history'
    r = post(url, json=data )
    r.raise_for_status()

def put_positions_history( data ):
    url = 'http://localhost:8083/blue-lion/write/positions-history/%d' % (data['id'])
    r = put(url, json=data )
    r.raise_for_status()

def post_transaction( data ):
    url = 'http://localhost:8083/blue-lion/write/transactions'
    r = post(url, json=data )
    r.raise_for_status()

def put_transaction( data ):
    url = 'http://localhost:8083/blue-lion/write/transactions/%d' % (data['id'])
    r = put(url, json=data )
    r.raise_for_status()

def projections_by_symbol( symbol ):
    url = 'http://localhost:8081/blue-lion/read/enriched-projections?symbol=%s' % (symbol)
    response = get(url)
    if response.status_code == 200:
        return response.json()
    return None

def projections_positions():
    url = 'http://localhost:8084/blue-lion/cache/enriched-projections-positions'
    response = get(url)
    if response.status_code == 200:
        return response.json()
    return None

def projections_watch():
    url = 'http://localhost:8084/blue-lion/cache/enriched-projections-watch'
    response = get(url)
    if response.status_code == 200:
        return response.json()
    return None

def projections_research():
    url = 'http://localhost:8084/blue-lion/cache/enriched-projections-research'
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
    # post_simfin_income({'date':'2019-12-13', 'ticker':'Mikey'})
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)