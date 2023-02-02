'''
Created on Jan 27, 2022

@author: scanlom
'''

'''
Summary:
Togabou -> Fujippi Migration. Backfills Togabou portfolios history to Fujippi. Note that
index, divisor, totalCashInfusion, costBasis, and accumulatedDividends values are left blank
to be populated by the transactions script

Togabou Touchpoints:
db.get_index_history_all
db.get_index_history
db.get_divisor_history
db.get_balance_history
db.get_portfolio_history_safe

Sanomaru Touchpoints:
_abl.portfolios_history_by_portfolio_id_date
_abl.post_portfolios_history

Prep:
delete from portfolios_history;
ALTER SEQUENCE portfolios_history_id_seq RESTART WITH 1;
'''

from api_database import database2
import api_blue_lion as _abl
from api_log import log

def populate_portfolios_history(db, index_from, balance_from, portfolio_from, index_tc_from, balance_tc_from, index_to, name_to):
	rows = db.get_index_history_all(index_from)
	for row in rows:
		try:
			index_tc = db.get_index_history(index_tc_from, row.date)
			divisor = db.get_divisor_history(index_from, row.date)
			divisor_tc = db.get_divisor_history(index_tc_from, row.date)
			total = db.get_balance_history(balance_from, row.date)
			total_tc = db.get_balance_history(balance_tc_from, row.date)
			cash = db.get_portfolio_history_safe(portfolio_from, db.CONST_SYMBOL_CASH, row.date)
			debt = db.get_portfolio_history_safe(portfolio_from, db.CONST_SYMBOL_DEBT, row.date)
			entry = {}
			entry['portfolioId'] = index_to
			entry['name'] = name_to
			entry['date'] = row.date.strftime('%Y-%m-%d')
			entry['index'] = row.value
			entry['indexTotalCapital'] = index_tc if index_tc is not None else 0
			entry['divisor'] = divisor if divisor is not None else 0
			entry['divisorTotalCapital'] = divisor_tc if divisor_tc is not None else 0
			entry['value'] = total if total is not None else 0
			entry['valueTotalCapital'] = total_tc if total_tc is not None else 0
			entry['cash'] = cash if cash is not None else 0
			entry['debt'] = debt if debt is not None else 0
			if _abl.portfolios_history_by_portfolio_id_date(index_to, entry['date']) is None:
				_abl.post_portfolios_history(entry)
		except Exception as err:
			print("Index %d Date %s" % (index_to, row.date.strftime('%Y-%m-%d')))
			log.exception(err)
			log.info("Aborted")

def main():
	log.info("Started...")

	db = database2()    
	populate_portfolios_history(db, db.CONST_INDEX_ROE, db.CONST_BALANCES_TYPE_TOTAL_ROE, db.CONST_PORTFOLIO_CASH, db.CONST_INDEX_ROTC, db.CONST_BALANCES_TYPE_TOTAL_ROTC, 1, "Total")
	populate_portfolios_history(db, db.CONST_INDEX_PLAY, db.CONST_BALANCES_TYPE_TOTAL_PLAY, db.CONST_PORTFOLIO_PLAY, db.CONST_INDEX_PLAY, db.CONST_BALANCES_TYPE_TOTAL_PLAY, 2, "Selfie")
	populate_portfolios_history(db, db.CONST_PORTFOLIO_OAK, db.CONST_BALANCES_TYPE_OAK, db.CONST_PORTFOLIO_OAK, db.CONST_PORTFOLIO_OAK, db.CONST_BALANCES_TYPE_OAK, 3, "Oak")
	populate_portfolios_history(db, db.CONST_INDEX_MANAGED, db.CONST_BALANCES_TYPE_TOTAL_MANAGED, db.CONST_PORTFOLIO_MANAGED, db.CONST_INDEX_MANAGED, db.CONST_BALANCES_TYPE_TOTAL_MANAGED, 4, "Managed")
	populate_portfolios_history(db, db.CONST_PORTFOLIO_RISK_ARB, db.CONST_BALANCES_TYPE_RISK_ARB, db.CONST_PORTFOLIO_RISK_ARB, db.CONST_PORTFOLIO_RISK_ARB, db.CONST_BALANCES_TYPE_RISK_ARB, 5, "Risk Arb")
	populate_portfolios_history(db, db.CONST_PORTFOLIO_TRADE_FIN, db.CONST_BALANCES_TYPE_TRADE_FIN, db.CONST_PORTFOLIO_TRADE_FIN, db.CONST_PORTFOLIO_TRADE_FIN, db.CONST_BALANCES_TYPE_TRADE_FIN, 6, "Trade Fin")
	populate_portfolios_history(db, db.CONST_PORTFOLIO_QUICK, db.CONST_BALANCES_TYPE_QUICK, db.CONST_PORTFOLIO_QUICK, db.CONST_PORTFOLIO_QUICK, db.CONST_BALANCES_TYPE_QUICK, 7, "Quick")
	populate_portfolios_history(db, db.CONST_INDEX_SELF, db.CONST_BALANCES_TYPE_TOTAL_SELF, db.CONST_PORTFOLIO_SELF, db.CONST_INDEX_SELF, db.CONST_BALANCES_TYPE_TOTAL_SELF, 8, "Portfolio")
	#populate_portfolios_history(db, db.CONST_PORTFOLIO_QUICK, 9, "None") <- None portfolio is added by the positions history script where needed

	log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")