'''
Created on Jan 27, 2022

@author: scanlom
'''

import datetime as _datetime
import json as _json
from api_database import database2
import api_blue_lion as _abl
import api_fundamentals as _af
from api_log import log

CONST_START_DATE    = _datetime.date(1999,8,1)
CONST_END_DATE    = _datetime.date(2022,3,1)

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + _datetime.timedelta(n)

def main():
	log.info("Started...")

	db = database2()
	actions = db.get_actions_by_type(db.CONST_ACTION_TYPE_CI_TOTAL)
	next_action = 0
	total_ci = 0
	for date in daterange(CONST_START_DATE, CONST_END_DATE):
		# If there is an action for today, process it first
		if actions[next_action].date.strftime("%Y-%m-%d") == date.strftime("%Y-%m-%d"):
			total_ci += actions[next_action].value1
			next_action += 1
			print(date.strftime("%Y-%m-%d") + " Portfolio %d Action Type %d Value %f" % (db.CONST_BLB_PORTFOLIO_TOTAL, db.CONST_ACTION_TYPE_CI_TOTAL, actions[next_action].value1))

		# If there is a portfolio history entry for today, populate the new cost basis
		portfolio_entry = _abl.portfolios_history_by_portfolio_id_date(db.CONST_BLB_PORTFOLIO_TOTAL, date.strftime("%Y-%m-%d"))
		if portfolio_entry is not None:
			portfolio_entry['costBasis'] = total_ci
			_abl.put_portfolios_history(portfolio_entry)
			#print(date.strftime("%Y-%m-%d") + " Portfolio %d updated") % (db.CONST_BLB_PORTFOLIO_TOTAL)

	log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")