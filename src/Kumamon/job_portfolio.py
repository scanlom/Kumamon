'''
Created on Jul 20, 2013

@author: scanlom
'''

from psycopg2 import connect
from psycopg2.extras import DictCursor
from api_config import config_database_connect
from api_database import database2
from api_log import log
import datetime as _datetime
import api_blue_lion as _abl

def format_ccy_sql(number):
    return str(round(number,2))

def calculate_total(db, portfolio):
    total = 0
    rows = db.get_constituents_by_portfolio(portfolio)
    for row in rows:
            total += row.value
    return total

def calculate_index(db, total, index):
    divisor = db.get_divisor(index)
    index = total*divisor
    return index    

def blb_portfolio(db, id, name, value, index, index_id, portfolio_id):
    divisor = db.get_divisor(index_id)
    cash = db.get_constituents_by_portfolio_symbol(portfolio_id, db.CONST_SYMBOL_CASH)
    portfolio = _abl.portfolio_by_id(id)

    # Update portfolio row
    _abl.put_portfolio({
        'id': id, 
        'name': name, 
        'value': value, 
        'index': index, 
        'divisor': divisor, 
        'cash': cash, 
        'debt': 0, 
        'valueTotalCapital': value, 
        'indexTotalCapital': index, 
        'divisorTotalCapital': divisor, 
        'model': portfolio['model'], 
        'active': True,
        })
    portfolio = _abl.portfolio_by_id(id)

    # Populate portfolio history row (add or update)
    date = _datetime.datetime.today().strftime('%Y-%m-%d')
    portfolio['portfolioId'] = id
    portfolio['date'] = date
    del portfolio['id']
    portfolio_history = _abl.portfolios_history_by_portfolio_id_date(id, date)
    if portfolio_history is None:
        _abl.post_portfolios_history(portfolio)
    else:
        portfolio['id'] = portfolio_history['id']
        _abl.put_portfolios_history(portfolio)

    # Populate positions
    rows = db.get_constituents_by_portfolio(portfolio_id)
    for row in rows:
        if row.symbol == db.CONST_SYMBOL_CASH:
            continue
        position = _abl.positions_by_symbol_portfolio_id(row.symbol, id)
        if position is not None:
            position['quantity'] = row.quantity if row.quantity is not None else 0
            position['price'] = row.price if row.price is not None else 0
            position['value'] = row.value if row.value is not None else 0
            position['model'] = row.model if row.model is not None else 0
            position['active'] = True
            print("Put " + row.symbol)
            _abl.put_position(position)
        else:
            position = {}
            refData = _abl.ref_data_by_symbol(row.symbol)
            position['refDataId'] = refData['id']
            position['portfolioId'] = id
            position['quantity'] = row.quantity if row.quantity is not None else 0
            position['price'] = row.price if row.price is not None else 0
            position['value'] = row.value if row.value is not None else 0
            position['model'] = row.model if row.model is not None else 0
            position['pricingType'] = row.pricing_type if row.pricing_type is not None else 1
            position['active'] = True
            print("Posted " + row.symbol)
            _abl.post_position(position)

def main():
    log.info("Started...")
    
    db = database2()
    
    total_play = calculate_total(db, db.CONST_PORTFOLIO_PLAY)
    index_play = calculate_index(db, total_play, db.CONST_INDEX_PLAY)
    total_managed = calculate_total(db, db.CONST_PORTFOLIO_MANAGED)
    index_managed = calculate_index(db, total_managed, db.CONST_INDEX_MANAGED)
    total_oak = calculate_total(db, db.CONST_PORTFOLIO_OAK)
    index_oak = calculate_index(db, total_oak, db.CONST_PORTFOLIO_OAK)
    total_risk_arb = calculate_total(db, db.CONST_PORTFOLIO_RISK_ARB)
    index_risk_arb = calculate_index(db, total_risk_arb, db.CONST_PORTFOLIO_RISK_ARB)
    total_trade_fin = calculate_total(db, db.CONST_PORTFOLIO_TRADE_FIN)
    index_trade_fin = calculate_index(db, total_trade_fin, db.CONST_PORTFOLIO_TRADE_FIN)
    total_quick = calculate_total(db, db.CONST_PORTFOLIO_QUICK)
    index_quick = calculate_index(db, total_quick, db.CONST_PORTFOLIO_QUICK)
    cash = db.get_constituents_by_portfolio_symbol(db.CONST_PORTFOLIO_CASH, db.CONST_SYMBOL_CASH)
    total_roe = total_play + total_oak + total_managed + total_risk_arb + total_trade_fin + total_quick + cash
    total_rotc = total_roe
    debt = db.get_constituents_by_portfolio_symbol(db.CONST_PORTFOLIO_CASH, db.CONST_SYMBOL_DEBT)
    total_roe -= debt
    index_roe = calculate_index(db, total_roe, db.CONST_INDEX_ROE)
    index_rotc = calculate_index(db, total_rotc, db.CONST_INDEX_ROTC)
    
    conn = connect( config_database_connect )
    cur = conn.cursor(cursor_factory=DictCursor)

    # Update index_history with today's values
    cur.execute("delete from index_history where date=current_date")
    cur.execute("insert into index_history values (current_date, 2, " + format_ccy_sql(index_roe) + ")")
    cur.execute("insert into index_history values (current_date, 3, " + format_ccy_sql(index_rotc) + ")")
    cur.execute("insert into index_history values (current_date, 4, " + format_ccy_sql(index_managed) + ")")
    cur.execute("insert into index_history values (current_date, 5, " + format_ccy_sql(index_play) + ")")
    cur.execute("insert into index_history values (current_date, 23, " + format_ccy_sql(index_oak) + ")")
    cur.execute("insert into index_history values (current_date, 24, " + format_ccy_sql(index_risk_arb) + ")")
    cur.execute("insert into index_history values (current_date, 25, " + format_ccy_sql(index_trade_fin) + ")")
    cur.execute("insert into index_history values (current_date, 26, " + format_ccy_sql(index_quick) + ")")
    conn.commit()
    
    # Update balances with today's values
    cur.execute("update balances set value=" + format_ccy_sql(total_roe) + " where type=12")
    cur.execute("update balances set value=" + format_ccy_sql(total_managed) + " where type=14")
    cur.execute("update balances set value=" + format_ccy_sql(total_rotc) + " where type=18")
    cur.execute("update balances set value=" + format_ccy_sql(total_play) + " where type=19")
    cur.execute("update balances set value=" + format_ccy_sql(total_oak) + " where type=23")
    cur.execute("update balances set value=" + format_ccy_sql(total_risk_arb) + " where type=24")
    cur.execute("update balances set value=" + format_ccy_sql(total_trade_fin) + " where type=25")
    cur.execute("update balances set value=" + format_ccy_sql(total_quick) + " where type=26")
    conn.commit()
    
    # Update balances_history with today's values
    cur.execute("delete from balances_history where date=current_date")
    cur.execute("insert into balances_history (select current_date, type, value from balances)")
    conn.commit()
    
    # Update portfolio_history with today's values
    cur.execute("delete from portfolio_history where date=current_date")
    cur.execute("insert into portfolio_history (select current_date, symbol, value, portfolio_id, pricing_type, quantity, price from constituents)")
    conn.commit()
    
    # Update divisors_history with today's values
    cur.execute("delete from divisors_history where date=current_date")
    cur.execute("insert into divisors_history (select current_date, type, value from divisors)")
    conn.commit()
    
    # Close the db
    cur.close()
    conn.close()
    
    # Blue Lion Bridge
    status = _abl.run_job_valuation_cut()
    log.info("BLB: Valuation Cut Successful, Status %d" % (status))

    '''_abl.put_portfolio({
        'id': 1, 
        'name': 'Total', 
        'value': total_roe, 
        'index': index_roe, 
        'divisor': db.get_divisor(db.CONST_INDEX_ROE), 
        'cash': cash, 
        'debt': debt, \
        'valueTotalCapital': total_rotc, 
        'indexTotalCapital': index_rotc, 
        'divisorTotalCapital': db.get_divisor(db.CONST_INDEX_ROTC), 
        'model': 0, 
        'active': True,
        })
    portfolio = _abl.portfolio_by_id(1)
    date = _datetime.datetime.today().strftime('%Y-%m-%d')
    portfolio['portfolioId'] = 1
    portfolio['date'] = date
    del portfolio['id']
    portfolio_history = _abl.portfolios_history_by_portfolio_id_date(1, date)
    if portfolio_history is None:
        _abl.post_portfolios_history(portfolio)
    else:
        portfolio['id'] = portfolio_history['id']
        _abl.put_portfolios_history(portfolio)

    blb_portfolio(db, 2, 'Selfie', total_play, index_play, db.CONST_INDEX_PLAY, db.CONST_PORTFOLIO_PLAY)
    blb_portfolio(db, 3, 'Oak', total_oak, index_oak, db.CONST_PORTFOLIO_OAK, db.CONST_PORTFOLIO_OAK)
    blb_portfolio(db, 4, 'Managed', total_managed, index_managed, db.CONST_INDEX_MANAGED, db.CONST_PORTFOLIO_MANAGED)
    blb_portfolio(db, 5, 'Risk Arb', total_risk_arb, index_risk_arb, db.CONST_PORTFOLIO_RISK_ARB, db.CONST_PORTFOLIO_RISK_ARB)
    blb_portfolio(db, 6, 'Trade Fin', total_trade_fin, index_trade_fin, db.CONST_PORTFOLIO_TRADE_FIN, db.CONST_PORTFOLIO_TRADE_FIN)
    blb_portfolio(db, 7, 'Quick', total_quick, index_quick, db.CONST_PORTFOLIO_QUICK, db.CONST_PORTFOLIO_QUICK)'''

    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")