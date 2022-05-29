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

CONST_START_DATE    = _datetime.date(2014,12,1)
CONST_END_DATE    = _datetime.date(2022,4,1)

CONST_TXN_TYPE_BUY = 1
CONST_TXN_TYPE_SELL = 2
CONST_TXN_TYPE_DIV = 3

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + _datetime.timedelta(n)

def process_action(db, next_index, actions, date, type, accumulated_dividends, cost_basis, divisor, index, total_cash_infusion, positions_by_symbol, positions_history_by_symbol, more_actions):
	if next_index < len(actions) and actions[next_index].date.strftime("%Y-%m-%d") == date.strftime("%Y-%m-%d"):
		symbol = actions[next_index].symbol
		if symbol not in positions_by_symbol:
			legacy_position = {
				'id': 0,
				'portfolioId': 0,
				'active': False,
			}
			positions_by_symbol[symbol] = legacy_position # MSTODO: have to get the legacy positions in for real
		position = positions_by_symbol[symbol]
		position_history = None
		if symbol in positions_history_by_symbol:
			position_history = positions_history_by_symbol[symbol]
		log.info(date.strftime("%Y-%m-%d") + " BLB Portfolio %d BLB Action Type %d Symbol %s Value %f" % (position['portfolioId'], type, symbol, actions[next_index].value1))

		# accumulated_dividends and total_cash_infusion so we can answer "what is our cash profit?" using the top level record
		if symbol not in accumulated_dividends:
			accumulated_dividends[symbol] = 0.0
		if symbol not in total_cash_infusion:
			total_cash_infusion[symbol] = 0.0

		# cost_basis so we can answer "what is our average price?" at the top level
		if symbol not in cost_basis:
			cost_basis[symbol] = 0.0

		if type is CONST_TXN_TYPE_BUY:
			total_cash_infusion[symbol] += float(actions[next_index].value1)
			cost_basis[symbol] += float(actions[next_index].value1)
			if symbol not in index:
				index[symbol] = float(actions[next_index].value1)
				divisor[symbol] = 1.0
			else:
				last_index = position_history['index']
				divisor[symbol] = last_index / ( position_history['value'] + float(actions[next_index].value1) )
				index[symbol] = last_index
		elif type is CONST_TXN_TYPE_SELL:
			total_cash_infusion[symbol] -= float(actions[next_index].value1)
			if actions[next_index].value2 == position_history['quantity']:
				cost_basis[symbol] = 0.0
				divisor[symbol] = 0.0
				index[symbol] = 0.0
			else:
				cost_basis[symbol] -= float(cost_basis[symbol]) * (float(actions[next_index].value2) / position_history['quantity'])
				last_index = position_history['index']
				divisor[symbol] = last_index / ( position_history['value'] - float(actions[next_index].value1) )
				index[symbol] = last_index
		else:
			accumulated_dividends[symbol] += float(actions[next_index].value1)
			# There are circumstances where a dividend occurs after a buy but before the buy has been entered in Togabou, so there is no
			# position_history object. We aren't going to go backfilling position_history objects that aren't in Togabou, so work around
			if position_history is not None:
				last_index = position_history['index']
				divisor[symbol] = last_index / ( position_history['value'] - float(actions[next_index].value1) )
				index[symbol] = position_history['value'] * divisor[symbol]
			else:
				last_index = index[symbol]
				divisor[symbol] = last_index / ( last_index - float(actions[next_index].value1) )
				index[symbol] = last_index * divisor[symbol]
		txn = {
			'date': date.strftime("%Y-%m-%d"),
			'type': type,
			'subType': 0,
			'positionId': position['id'],
			'portfolioId': position['portfolioId'],
			'value': float(actions[next_index].value1),
			'quantity': float(actions[next_index].value2),
			'positionAfter': {
				'symbol': symbol,
				'costBasis': cost_basis[symbol],
				'totalCashInfusion': total_cash_infusion[symbol],
				'accumulatedDividends': accumulated_dividends[symbol],
				'divisor': divisor[symbol],
				'index': index[symbol],
				}
		}
		_abl.post_transaction(txn)
		more_actions = True
		next_index += 1
	return next_index, more_actions

def main():
	log.info("Started...")

	db = database2()
	portfolio_blb_id = db.CONST_BLB_PORTFOLIO_SELFIE
	portfolio_id = db.CONST_PORTFOLIO_PLAY
	positions = _abl.enriched_positions_by_portfolio_id(portfolio_blb_id)
	positions_by_symbol = {}
	for position in positions:
		positions_by_symbol[position['symbol']] = position
	buys = db.get_actions_by_type_portfolio_id(db.CONST_ACTION_TYPE_BOUGHT, portfolio_id)
	sells = db.get_actions_by_type_portfolio_id(db.CONST_ACTION_TYPE_SOLD, portfolio_id)
	divs = db.get_actions_by_type_portfolio_id(db.CONST_ACTION_TYPE_DIVIDEND, portfolio_id)
	next_buy = 0
	next_sell = 0
	next_div = 0
	cost_basis = {}
	divisor = {}
	index = {}
	total_cash_infusion = {}
	accumulated_dividends = {}
	positions_history_by_symbol = {}
	for date in daterange(CONST_START_DATE, CONST_END_DATE):
		log.info("Processing " + date.strftime("%Y-%m-%d"))

		# MSTODO - Also verify quantities stay in line
		# If there are actions for today, process them first (can be multiple)
		more_actions = True
		while more_actions is True:
			more_actions = False
			next_buy, more_actions = process_action(db, next_buy, buys, date, CONST_TXN_TYPE_BUY, accumulated_dividends, cost_basis, divisor, index, total_cash_infusion, positions_by_symbol, positions_history_by_symbol, more_actions)
			next_sell, more_actions = process_action(db, next_sell, sells, date, CONST_TXN_TYPE_SELL, accumulated_dividends, cost_basis, divisor, index, total_cash_infusion, positions_by_symbol, positions_history_by_symbol, more_actions)
			next_div, more_actions = process_action(db, next_div, divs, date, CONST_TXN_TYPE_DIV, accumulated_dividends, cost_basis, divisor, index, total_cash_infusion, positions_by_symbol, positions_history_by_symbol, more_actions)

		# If there are any positions history entries for today, populate the new data and save the entry for later use
		# Note - These are handled after actions, because under Togabou the action may have been handled and then history entry recreated (job_portfolio.py)
		positions_histories = _abl.enriched_positions_history_by_portfolio_id_date(portfolio_blb_id, date.strftime("%Y-%m-%d"))
		if positions_histories is not None:
			for position_history in positions_histories:
				symbol = position_history['symbol']
				positions_history_by_symbol[symbol] = position_history
				position_history['costBasis'] = cost_basis[symbol]
				position_history['totalCashInfusion'] = total_cash_infusion[symbol]
				position_history['accumulatedDividends'] = accumulated_dividends[symbol]
				position_history['divisor'] = divisor[symbol]
				position_history['index'] = position_history['value'] * divisor[symbol]
				_abl.put_portfolios_history(position_history)

				# Keep the most updated history entry for use in transaction processing
				positions_history_by_symbol[symbol] = position_history

	log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")