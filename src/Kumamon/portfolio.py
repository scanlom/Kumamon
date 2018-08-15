'''
Created on Jul 20, 2013

@author: scanlom
'''

import database
from api_config import config_database_connect
from api_database import database2
from api_log import log
from decimal import *
import psycopg2     # Postgresql access
import psycopg2.extras  # Postgresql access
from datetime import datetime
from datetime import timedelta
from time import localtime, strftime       # Time

CONST_ONE_UNIT  = Decimal(203508.28)

def format_ccy(number):
    return '"' + '{0:,.2f}'.format(number) + '"'

def format_ccy_plain(number):
    return '{0:,.2f}'.format(number)

def format_ccy_sql(number):
    return str(round(number,2))

def format_pct(number):
    return '%{0:,.2f}'.format(100*number)

def get_ytd_balance_base(cur):
    now = datetime.now()
    date = "01/01/" + str(now.year)
    if now.month == 1 and now.day == 1:
        date = "01/01/" + str(now.year - 1)
    return database.get_scalar("select * from balances_history where type=12 and date='" + date + "'", cur)

def get_ytd_base(index, cur):
    now = datetime.now()
    date = "01/01/" + str(now.year)
    if now.month == 1 and now.day == 1:
        date = "01/01/" + str(now.year - 1)
    return database.get_scalar("select * from index_history where type=" + str(index) + " and date='" + date + "'", cur)

def get_qtd_base(index, cur):
    now = datetime.now()
    date = "10/01/" + str(now.year - 1)
    if now.month > 9 and not (now.month == 10 and now.day == 1):
        date = "10/01/" + str(datetime.now().year)
    elif datetime.now().month > 6 and not (now.month == 7 and now.day == 1):
        date = "07/01/" + str(datetime.now().year)
    elif datetime.now().month > 3 and not (now.month == 4 and now.day == 1):
        date = "04/01/" + str(datetime.now().year)
    elif not (now.month == 1 and now.day == 1):
        date = "01/01/" + str(datetime.now().year)

    return database.get_scalar("select * from index_history where type=" + str(index) + " and date='" + date + "'", cur)

def get_day_base(index, cur):
    yesterday = datetime.now() - timedelta(days=1)
    date = yesterday.strftime("%m/%d/%Y")
    return database.get_scalar("select * from index_history where type=" + str(index) + " and date='" + date + "'", cur)

def main():
    log.info("Started...")
    
    conn = psycopg2.connect( config_database_connect )
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = "select * from constituents where portfolio_id=1 and pricing_type=1";
    cur.execute(sql)
    rows = cur.fetchall()   
        
    total_self = 0
    for row in rows:
            total_self += row['value']

    sql = "select * from constituents where portfolio_id=1 and symbol='CASH'";
    cur.execute(sql)
    rows = cur.fetchall()  
    total_self += rows[0]['value']
    
    divisor = database.get_scalar("select * from divisors where type=1", cur)
    index_self = total_self*divisor

    # Lazy for now - copy paste to calculate play money portfolio
    sql = "select * from constituents where portfolio_id=5 and pricing_type=1";
    cur.execute(sql)
    rows = cur.fetchall()   
        
    total_play = 0
    for row in rows:
            total_play += row['value']

    sql = "select * from constituents where portfolio_id=5 and symbol='CASH'";
    cur.execute(sql)
    rows = cur.fetchall()  
    total_play += rows[0]['value']
    
    divisor = database.get_scalar("select * from divisors where type=5", cur)
    index_play = total_play * divisor

    sql = "select * from constituents where portfolio_id=2 and pricing_type=1";
    cur.execute(sql)
    rows = cur.fetchall()   
        
    total_managed = 0
    for row in rows:
            total_managed += row['value']

    sql = "select * from constituents where portfolio_id=2 and pricing_type=2";
    cur.execute(sql)
    rows = cur.fetchall()   
    
    for row in rows:
            total_managed += row['value']
    
    divisor = database.get_scalar("select * from divisors where type=4", cur)
    index_managed = total_managed*divisor

    cash = database.get_scalar("select * from constituents where portfolio_id=3 and symbol='CASH'", cur)
    total_roe = total_self + total_managed + cash
    total_rotc = total_roe  

    debt = database.get_scalar("select * from constituents where portfolio_id=3 and symbol='DEBT'", cur)
    total_roe -= debt 

    divisor = database.get_scalar("select * from divisors where type=2", cur)
    index_roe = total_roe*divisor

    divisor = database.get_scalar("select * from divisors where type=3", cur)
    index_rotc = total_rotc*divisor

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