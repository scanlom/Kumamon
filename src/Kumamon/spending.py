'''
Created on Jul 14, 2013

@author: scanlom
'''

import mail, database, psycopg2, psycopg2.extras, config
from datetime import datetime, timedelta
from time import localtime, strftime       # Time
from log import log

def format_ccy(number):
    return '{0:,.2f}'.format(number)

def main():
    log.info("Started...")
    conn = psycopg2.connect( config.config_database_connect )
    
    db = database.finances()
    cash = db.recon_budget()
    fumi_cash = cash
    body = """\
<html>
<head></head>
<body><p>Cash is """ + str(cash) + """, Fumi Cash is """ + format_ccy(fumi_cash) + """<br></p>
<p>Current budget is<br></p>
<table border="1">
<tr><td>Rent</td><td>3,337.63</td></tr>
<tr><td>Utilities</td><td>200.00</td></tr>
<tr><td>Misc</td><td>2,769.77</td></tr>
</table>    
<p>Spending for last seven days<br></p><table border="1">"""
    
    foo = datetime.now() - timedelta(days=7)
    
    sql = """select tt.description, s.amount from 
    (
        select s.type as type, sum(s.amount) as amount from spending s 
        where s.date >= '""" + foo.strftime("%m/%d/%Y") + """' 
        group by s.type 
    ) as s, spending_types tt where s.type = tt.type order by s.amount desc"""

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql)
    rows = cur.fetchall()    
    
    for row in rows:
       body += "<tr><td>" + row['description'] + "</td><td>" + str(row['amount']) + "</td></tr>"
       
    body += """</table><p>Spending for last thirty days<br></p><table border="1">"""
    foo = datetime.now() - timedelta(days=30)
    
    sql = """select tt.description, s.amount from 
    (
        select s.type as type, sum(s.amount) as amount from spending s 
        where s.date >= '""" + foo.strftime("%m/%d/%Y") + """' 
        group by s.type 
    ) as s, spending_types tt where s.type = tt.type order by s.amount desc"""

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql)
    rows = cur.fetchall()    
    
    for row in rows:
       body += "<tr><td>" + row['description'] + "</td><td>" + str(row['amount']) + "</td></tr>"
       
    body += """</table><p>Summary for last thirty days<br></p><table border="1">"""
     
    sql = """select s.date, s.amount, s.description, tt.description as type, st.description as source
    from spending s, spending_types tt, balances st
    where date >= '""" + foo.strftime("%m/%d/%Y") + """' and 
        tt.Type = s.type and
        st.Type = s.source
        order by date desc"""

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql)
    rows = cur.fetchall()    
    
    for row in rows:
       body += "<tr><td>" + str(row['date']) + "</td><td>" + str(row['amount']) + "</td><td>" + row['description'] + "</td><td>" + row['type'] +"</td><td>" + row['source'] +"</td></tr>" 
      
    body += """</table></body></html>""";
    subject = 'Spending Report - ' + strftime("%Y-%m-%d", localtime())
     
    mail.send_mail_html_self(subject, body)    
    
    subject = 'Budget left is - ' + format_ccy(fumi_cash)
    body = 'Hello Blue!'
    
    mail.send_mail_html_fumi(subject, body) 
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
        mail.send_mail_html_self("FAILURE:  Spending.py", str( err ) ) 