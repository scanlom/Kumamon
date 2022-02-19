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

def populate_portfolios_history(db, index_from, index_to):
	rows = db.get_index_history_all(index_from)
	for row in rows:
		entry = {}
		entry['portfolioId'] = index_to
		entry['date'] = row.date.strftime('%Y-%m-%d')
		entry['index'] = row.value
		if _abl.portfolios_history_by_portfolio_id_date(index_to, entry['date']) is None:
			_abl.post_portfolios_history(entry)

def main():
	log.info("Started...")

	db = database2()    
	populate_portfolios_history(db, db.CONST_INDEX_ROE, 1)
	populate_portfolios_history(db, db.CONST_INDEX_PLAY, 2)
	populate_portfolios_history(db, db.CONST_PORTFOLIO_OAK, 3)
	populate_portfolios_history(db, db.CONST_INDEX_MANAGED, 4)
	populate_portfolios_history(db, db.CONST_PORTFOLIO_RISK_ARB, 5)
	populate_portfolios_history(db, db.CONST_PORTFOLIO_TRADE_FIN, 6)
	populate_portfolios_history(db, db.CONST_PORTFOLIO_QUICK, 7)

	log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")