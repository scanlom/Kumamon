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
    
    total_self = calculate_total(db, db.CONST_PORTFOLIO_SELF)
    index_self = calculate_index(db, total_self, db.CONST_INDEX_SELF)
    total_play = calculate_total(db, db.CONST_PORTFOLIO_PLAY)
    index_play = calculate_index(db, total_play, db.CONST_INDEX_PLAY)
    total_managed = calculate_total(db, db.CONST_PORTFOLIO_MANAGED)
    index_managed = calculate_index(db, total_managed, db.CONST_INDEX_MANAGED)
    cash = db.get_constituents_by_portfolio_symbol(db.CONST_PORTFOLIO_CASH, db.CONST_SYMBOL_CASH)
    total_roe = total_self + total_managed + cash
    total_rotc = total_roe
    debt = db.get_constituents_by_portfolio_symbol(db.CONST_PORTFOLIO_CASH, db.CONST_SYMBOL_DEBT)
    total_roe -= debt
    index_roe = calculate_index(db, total_roe, db.CONST_INDEX_ROE)
    index_rotc = calculate_index(db, total_rotc, db.CONST_INDEX_ROTC)
    
    conn = connect( config_database_connect )
    cur = conn.cursor(cursor_factory=DictCursor)

    # Update index_history with today's values
    cur.execute("delete from index_history where date=current_date")
    cur.execute("insert into index_history values (current_date, 1, " + format_ccy_sql(index_self) + ")")
    cur.execute("insert into index_history values (current_date, 2, " + format_ccy_sql(index_roe) + ")")
    cur.execute("insert into index_history values (current_date, 3, " + format_ccy_sql(index_rotc) + ")")
    cur.execute("insert into index_history values (current_date, 4, " + format_ccy_sql(index_managed) + ")")
    cur.execute("insert into index_history values (current_date, 5, " + format_ccy_sql(index_play) + ")")
    conn.commit()
    
    # Update balances with today's values
    cur.execute("update balances set value=" + format_ccy_sql(total_roe) + " where type=12")
    cur.execute("update balances set value=" + format_ccy_sql(total_self) + " where type=13")
    cur.execute("update balances set value=" + format_ccy_sql(total_managed) + " where type=14")
    cur.execute("update balances set value=" + format_ccy_sql(total_rotc) + " where type=18")
    cur.execute("update balances set value=" + format_ccy_sql(total_play) + " where type=19")
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