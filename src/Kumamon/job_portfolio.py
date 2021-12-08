'''
Created on Jul 20, 2013

@author: scanlom
'''

from psycopg2 import connect
from psycopg2.extras import DictCursor
from api_config import config_database_connect
from api_database import database2
from api_log import log

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
    
    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")