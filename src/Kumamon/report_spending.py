'''
Created on Jul 14, 2013

@author: scanlom
'''

from datetime import datetime
from datetime import timedelta
from time import localtime
from time import strftime
from api_database import database2
from api_log import log
from api_mail import send_mail_html_self
from api_reporting import report

def append_budget_row( db, table, name, types, budget ):
    day_of_year = datetime.now().timetuple().tm_yday
    spending = db.get_ytd_spending_sum( types )
    projected = spending * 365 / day_of_year
    table.append( [ name, spending, projected, budget, budget - projected ] )

def main():
    log.info("Started...")
    db = database2()
    rpt = report()
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY, rpt.CONST_FORMAT_CCY]
    table = [
        [ "Category", "Spent", "Projected", "Budget", "Tracking" ],
        ]
    append_budget_row( db, table, "Base", [0,2,3,4,5,8,12,96], 65000 )
    append_budget_row( db, table, "Rent", [1], 42000 )
    append_budget_row( db, table, "Travel", [7], 10000 )
    append_budget_row( db, table, "Helper", [9], 12000 )
    append_budget_row( db, table, "Monchichi", [94], 12000 )
    append_budget_row( db, table, "Fumi", [11], 5000 )
    append_budget_row( db, table, "Mike", [6,10], 5000 )
    append_budget_row( db, table, "Special", [93,95,97,98,99], 0 )
    append_budget_row( db, table, "Total", [0,1,2,3,4,5,6,7,8,9,10,11,12,93,94,95,96,97,98,99], 151000 )
    rpt.add_table(table, formats)

    #format_budget_row( db, "Recon", "select distinct type from spending", Decimal( '151000.00' ), day_of_year ) + \
    rpt.add_string("Summary for last thirty days")
    
    """ 
    sql = select s.date, s.amount, s.description, st.description as type, b.description as source
    from spending s, spending_types st, balances b
    where date >= ' + thirty_days_ago.strftime("%m/%d/%Y") + ' and 
        st.type = s.type and
        b.type = s.source and
        s.type in (0,1,2,3,4,5,8,9)
        order by date desc

    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute(sql)
    rows = cur.fetchall()    
    
    for row in rows:
       body += "<tr><td>" + str(row['date']) + "</td><td style='text-align:right'>" + format_ccy( row['amount'] ) + "</td><td>" + row['description'] + "</td><td>" + row['type'] +"</td><td>" + row['source'] +"</td></tr>" 
    """  
    subject = 'Spending Report - ' + strftime("%Y-%m-%d", localtime())
     
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
        send_mail_html_self("FAILURE:  Spending.py", str( err ) ) 