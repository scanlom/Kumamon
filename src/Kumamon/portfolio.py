'''
Created on Jul 20, 2013

@author: scanlom
'''

import mail, database, config
from log import log
import psycopg2     # Postgresql access
import psycopg2.extras  # Postgresql access
from datetime import datetime
from datetime import timedelta
from time import localtime, strftime       # Time

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
    
    csv = ""
    conn = psycopg2.connect( config.config_database_connect )
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = "select * from constituents where portfolio_id=1 and pricing_type=1";
    cur.execute(sql)
    rows = cur.fetchall()   
        
    total_self = 0
    for row in rows:
            total_self += row['value']
            csv += row['symbol'] + "," + str(row['quantity']) + "," + format_ccy(row['price']) + "," + format_ccy(row['value']) + "\n"

    sql = "select * from constituents where portfolio_id=1 and symbol='CASH'";
    cur.execute(sql)
    rows = cur.fetchall()  
    total_self += rows[0]['value']
    csv += rows[0]['symbol'] + ",,," + format_ccy(rows[0]['value']) + "\n"
    csv += "TOTAL,,," + format_ccy(total_self) + "\n"
    
    divisor = database.get_scalar("select * from divisors where type=1", cur)
    index_self = total_self*divisor
    csv += ",," + str(divisor) + "," + format_ccy(index_self) + "\n\n"

    # Lazy for now - copy paste to calculate play money portfolio
    sql = "select * from constituents where portfolio_id=5 and pricing_type=1";
    cur.execute(sql)
    rows = cur.fetchall()   
        
    total_play = 5
    for row in rows:
            total_play += row['value']
            csv += row['symbol'] + "," + str(row['quantity']) + "," + format_ccy(row['price']) + "," + format_ccy(row['value']) + "\n"

    sql = "select * from constituents where portfolio_id=5 and symbol='CASH'";
    cur.execute(sql)
    rows = cur.fetchall()  
    total_play += rows[0]['value']
    csv += rows[0]['symbol'] + ",,," + format_ccy(rows[0]['value']) + "\n"
    csv += "TOTAL,,," + format_ccy(total_play) + "\n"
    
    divisor = database.get_scalar("select * from divisors where type=5", cur)
    index_play = total_play * divisor
    csv += ",," + str(divisor) + "," + format_ccy(index_play) + "\n\n"

    sql = "select * from constituents where portfolio_id=2 and pricing_type=1";
    cur.execute(sql)
    rows = cur.fetchall()   
        
    total_managed = 0
    for row in rows:
            total_managed += row['value']
            csv += row['symbol'] + "," + str(row['quantity']) + "," + format_ccy(row['price']) + "," + format_ccy(row['value']) + "\n"

    sql = "select * from constituents where portfolio_id=2 and pricing_type=2";
    cur.execute(sql)
    rows = cur.fetchall()   
    
    for row in rows:
            total_managed += row['value']
            csv += row['symbol'] + ",,," + format_ccy(row['value']) + "\n"
    
    csv += "TOTAL,,," + str(total_managed) + "\n"
    
    divisor = database.get_scalar("select * from divisors where type=4", cur)
    index_managed = total_managed*divisor
    csv += ",," + str(divisor) + "," + format_ccy(index_managed) + "\n\n"        

    cash = database.get_scalar("select * from constituents where portfolio_id=3 and symbol='CASH'", cur)
    total_roe = total_self + total_managed + cash
    total_rotc = total_roe  
    csv += "CASH,,," + format_ccy(cash) + "\n"

    debt = database.get_scalar("select * from constituents where portfolio_id=3 and symbol='DEBT'", cur)
    total_roe -= debt 
    csv += "DEBT,,," + format_ccy(debt) + "\n"

    divisor = database.get_scalar("select * from divisors where type=2", cur)
    index_roe = total_roe*divisor
    csv += "Total (ROE)," + format_ccy(total_roe) + "," + str(divisor) + "," + format_ccy(index_roe) + "\n"

    divisor = database.get_scalar("select * from divisors where type=3", cur)
    index_rotc = total_rotc*divisor
    csv += "Total (ROTC)," + format_ccy(total_rotc) + "," + str(divisor) + "," + format_ccy(index_rotc) + "\n"

    # Top the csv with the performance table
    perf = ",YTD,QTD,Day\n"
    perf += "Total (ROE)," + format_pct(index_roe/get_ytd_base(2, cur)-1) + "," 
    perf +=  format_pct(index_roe/get_qtd_base(2, cur)-1) + ","
    perf +=  format_pct(index_roe/get_day_base(2, cur)-1) + "\n"
    perf += "Total (ROTC)," + format_pct(index_rotc/get_ytd_base(3, cur)-1) + "," 
    perf +=  format_pct(index_rotc/get_qtd_base(3, cur)-1) + ","
    perf +=  format_pct(index_rotc/get_day_base(3, cur)-1) + "\n"
    perf += "Self," + format_pct(index_self/get_ytd_base(1, cur)-1) + "," 
    perf +=  format_pct(index_self/get_qtd_base(1, cur)-1) + ","
    perf +=  format_pct(index_self/get_day_base(1, cur)-1) + "\n"
    perf += "Managed," + format_pct(index_managed/get_ytd_base(4, cur)-1) + "," 
    perf +=  format_pct(index_managed/get_qtd_base(4, cur)-1) + ","
    perf +=  format_pct(index_managed/get_day_base(4, cur)-1) + "\n\n"
    csv = perf + csv

    print(csv)
     
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
    
    # Determine cash made this year
    profit = total_roe - get_ytd_balance_base(cur) - database.get_scalar("select * from balances where type=17", cur)
    
    # Send a summary mail
    subject = "Portfolio Summary - Total (ROE) " + format_pct(index_roe/get_day_base(2, cur)-1)
    subject += " Self " + format_pct(index_self/get_day_base(1, cur)-1)    
    
    body = """\
<html>
<head></head>
<body><table border="1">
<tr><td></td><td>YTD</td><td>QTD</td><td>Day</td></tr>"""
    body += "<tr><td>Total (ROE)</td><td>" + format_pct(index_roe/get_ytd_base(2, cur)-1) + "</td>" 
    body += "<td>" + format_pct(index_roe/get_qtd_base(2, cur)-1) + "</td>"
    body += "<td>" + format_pct(index_roe/get_day_base(2, cur)-1) + "</td></tr>"
    body += "<tr><td>Total (ROTC)</td><td>" + format_pct(index_rotc/get_ytd_base(3, cur)-1) + "</td>" 
    body += "<td>" + format_pct(index_rotc/get_qtd_base(3, cur)-1) + "</td>"
    body += "<td>" + format_pct(index_rotc/get_day_base(3, cur)-1) + "</td></tr>"
    body += "<tr><td>Self</td><td>" + format_pct(index_self/get_ytd_base(1, cur)-1) + "</td>" 
    body += "<td>" + format_pct(index_self/get_qtd_base(1, cur)-1) + "</td>"
    body += "<td>" + format_pct(index_self/get_day_base(1, cur)-1) + "</td></tr>"
    body += "<tr><td>Play</td><td>" + format_pct(index_play/get_ytd_base(5, cur)-1) + "</td>" 
    body += "<td>" + format_pct(index_play/get_qtd_base(5, cur)-1) + "</td>"
    body += "<td>" + format_pct(index_play/get_day_base(5, cur)-1) + "</td></tr>"
    body += "<tr><td>Managed</td><td>" + format_pct(index_managed/get_ytd_base(4, cur)-1) + "</td>" 
    body += "<td>" + format_pct(index_managed/get_qtd_base(4, cur)-1) + "</td>"
    body += "<td>" + format_pct(index_managed/get_day_base(4, cur)-1) + "</td></tr>"
    body += "</table>Profit: " + format_ccy_plain(profit) + "</body></html>"

    # Close the db
    cur.close()
    conn.close()
    
    mail.send_mail_html_self(subject, body)
    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
        mail.send_mail_html_self("FAILURE:  portfolio.py", str( err ) ) 
        
            