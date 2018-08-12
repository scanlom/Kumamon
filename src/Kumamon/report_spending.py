'''
Created on Jul 14, 2013

@author: scanlom
'''

from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from time import localtime
from time import strftime
from psycopg2 import connect
from psycopg2.extras import DictCursor
from api_config import config_database_connect
from api_log import log
from api_mail import send_mail_html_self
from database import finances


def format_ccy( number ):
    return '{0:,.2f}'.format( number )

def format_budget_row( db, name, where, total, day_of_year ):
    current = db.get_spending_sum( where )
    projected = current * 365 / day_of_year
    tracking = total - projected
    return "<tr><td>" + name + "</td><td style='text-align:right'>" + format_ccy( current ) + \
        "</td><td style='text-align:right'>" + format_ccy( projected ) + "</td><td style='text-align:right'>" + \
        format_ccy( total ) + "</td><td style='text-align:right'>" + format_ccy( tracking ) + "</td></tr>"

def main():
    log.info("Started...")
    conn = connect( config_database_connect )
    db = finances()
    day_of_year = datetime.now().timetuple().tm_yday
    thirty_days_ago = datetime.now() - timedelta(days=30)
   
    body = """
<html>
<head></head>
<body>
<p>Current budget is<br></p>
<table border="1"><tr><th>Category</th><th>Spent</th><th>Projected</th><th>Budget</th><th>Tracking</th></tr>""" + \
    format_budget_row( db, "Base", "0,2,3,4,5,8,12,96", Decimal( '65000' ), day_of_year ) + \
    format_budget_row( db, "Rent", "1", Decimal( '42000' ), day_of_year ) + \
    format_budget_row( db, "Travel", "7", Decimal( '10000' ), day_of_year ) + \
    format_budget_row( db, "Helper", "9", Decimal( '12000' ), day_of_year ) + \
    format_budget_row( db, "Monchichi", "94", Decimal( '12000' ), day_of_year ) + \
    format_budget_row( db, "Fumi", "11", Decimal( '5000.00' ), day_of_year ) + \
    format_budget_row( db, "Mike", "6,10", Decimal( '5000.00' ), day_of_year ) + \
    format_budget_row( db, "Special", "93,95,97,98,99", Decimal( '0.00' ), day_of_year ) + \
    format_budget_row( db, "Total", "0,1,2,3,4,5,6,7,8,9,10,11,12,93,94,95,96,97,98,99", Decimal( '151000.00' ), day_of_year ) + \
    format_budget_row( db, "Recon", "select distinct type from spending", Decimal( '151000.00' ), day_of_year ) + \
"""</table>"""
    body += """</table><p>Summary for last thirty days<br></p><table border="1">"""
     
    sql = """select s.date, s.amount, s.description, st.description as type, b.description as source
    from spending s, spending_types st, balances b
    where date >= '""" + thirty_days_ago.strftime("%m/%d/%Y") + """' and 
        st.type = s.type and
        b.type = s.source and
        s.type in (0,1,2,3,4,5,8,9)
        order by date desc"""

    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(sql)
    rows = cur.fetchall()    
    
    for row in rows:
       body += "<tr><td>" + str(row['date']) + "</td><td style='text-align:right'>" + format_ccy( row['amount'] ) + "</td><td>" + row['description'] + "</td><td>" + row['type'] +"</td><td>" + row['source'] +"</td></tr>" 
      
    body += """</table></body></html>""";
    subject = 'Spending Report - ' + strftime("%Y-%m-%d", localtime())
     
    send_mail_html_self(subject, body)
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
        send_mail_html_self("FAILURE:  Spending.py", str( err ) ) 