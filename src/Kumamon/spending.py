'''
Created on Jul 14, 2013

@author: scanlom
'''

import mail, database, psycopg2, psycopg2.extras, config
from datetime import datetime, timedelta
from time import localtime, strftime       # Time
from log import log
from decimal import *

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
    conn = psycopg2.connect( config.config_database_connect )
    db = database.finances()
    day_of_year = datetime.now().timetuple().tm_yday
    thirty_days_ago = datetime.now() - timedelta(days=30)
   
    body = """
<html>
<head></head>
<body>
<p>Current budget is<br></p>
<table border="1"><tr><th>Category</th><th>Spent</th><th>Projected</th><th>Budget</th><th>Tracking</th></tr>""" + \
    format_budget_row( db, "Budget", "0,2,3,4,5,8,9", Decimal( '53247.44' ), day_of_year ) + \
    format_budget_row( db, "Fumi", "11", Decimal( '9165.29' ), day_of_year ) + \
    format_budget_row( db, "Mike", "6,10", Decimal( '5000.00' ), day_of_year ) + \
    format_budget_row( db, "Special", "7,94,95,96,97,98,99", Decimal( '10000.00' ), day_of_year ) + \
    format_budget_row( db, "Rent", "1", Decimal( '41752.56' ), day_of_year ) + \
"""</table>"""
    body += """</table><p>Summary for last thirty days<br></p><table border="1">"""
     
    sql = """select s.date, s.amount, s.description, st.description as type, b.description as source
    from spending s, spending_types st, balances b
    where date >= '""" + thirty_days_ago.strftime("%m/%d/%Y") + """' and 
        st.type = s.type and
        b.type = s.source and
        s.type in (0,1,2,3,4,5,8,9)
        order by date desc"""

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql)
    rows = cur.fetchall()    
    
    for row in rows:
       body += "<tr><td>" + str(row['date']) + "</td><td style='text-align:right'>" + format_ccy( row['amount'] ) + "</td><td>" + row['description'] + "</td><td>" + row['type'] +"</td><td>" + row['source'] +"</td></tr>" 
      
    body += """</table></body></html>""";
    subject = 'Spending Report - ' + strftime("%Y-%m-%d", localtime())
     
    mail.send_mail_html_self(subject, body)
    mail.send_mail_html_fumi(subject, body)
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
        mail.send_mail_html_self("FAILURE:  Spending.py", str( err ) ) 