'''
Created on Jul 20, 2013

@author: scanlom
'''

import database
from api_config import config_database_connect
from api_database import database2
from api_log import log
from api_mail import send_mail_html_self
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

        

    
    
    # Determine cash made this year
    profit = total_roe - get_ytd_balance_base(cur) - database.get_scalar("select * from balances where type=17", cur)

    # Send a summary mail
    subject = "Profit - " + format_ccy_plain(profit) + " / " + format_pct(index_roe/get_ytd_base(2, cur)-1)
    
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
    body += "</table>"
    body += "One Unit (" + format_ccy_plain(CONST_ONE_UNIT) + ") - " + format_pct(CONST_ONE_UNIT / total_roe) + "<br>"
    body += "One Million - " + format_pct(1000000 / total_roe) + "<br>"
    
    db2 = database2()
    row_base_roe_5 = db2.get_index_row_minus_years(database2.CONST_INDEX_ROE, 5)
    row_base_roe_10 = db2.get_index_row_minus_years(database2.CONST_INDEX_ROE, 10)
    
    cagr_five = ( ( index_roe / row_base_roe_5.value ) ** Decimal(0.2) ) - 1
    cagr_ten = ( ( index_roe / row_base_roe_10.value ) ** Decimal(0.1) ) - 1
    inflect_five = total_roe * cagr_five - CONST_ONE_UNIT
    inflect_ten = total_roe * cagr_ten - CONST_ONE_UNIT
    if inflect_five > 0:
        body += "Five Inflection - " + format_pct(cagr_five) + ", <font color='green'>" + format_ccy_plain( inflect_five ) + "</font><br>"
    else:
        body += "Five Inflection - " + format_pct(cagr_five) + ", <font color='red'>" + format_ccy_plain( inflect_five ) + "</font><br>"
    if inflect_ten > 0:
        body += "Ten Inflection - " + format_pct(cagr_ten) + ", <font color='green'>" + format_ccy_plain( inflect_ten ) + "</font><br>"
    else:
        body += "Ten Inflection - " + format_pct(cagr_ten) + ", <font color='red'>" + format_ccy_plain( inflect_ten ) + "</font><br>"
    body += "</body></html>"

    # Close the db
    cur.close()
    conn.close()
    
    send_mail_html_self(subject, body)
    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
        send_mail_html_self("FAILURE:  portfolio.py", str( err ) ) 