'''
Created on Jan 27, 2022

@author: scanlom
'''

'''
Summary:
Togabou -> Fujippi Migration. Backfills Togabou actions to Fujippi transactions, also updates Fujippi position_history and portfolios_history with
index, divisor, totalCashInfusion, costBasis, and accumulatedDividends values

Togabou Touchpoints:
db.get_actions_by_type_portfolio_id

Sanomaru Touchpoints:
_abl.post_transaction
_abl.enriched_positions_by_portfolio_id
_abl.enriched_positions_history_by_portfolio_id_date
_abl.put_portfolios_history

Prep:
1. Ensure positions_history and portfolios_history are up to date
2. Run:
delete from transactions;
ALTER SEQUENCE transactions_id_seq RESTART WITH 1;
'''

from copy import copy, deepcopy
import datetime as _datetime
from Kumamon.common.api_database import database2
import api_blue_lion as _abl
from api_log import log

CONST_START_DATE    	= _datetime.date(1999,8,1)
CONST_END_DATE    		= _datetime.date(2023,2,5)
CONST_TRACK_POS_INDEX 	= [ 2,3,5,6,7,8 ] # Don't track position level indices for Managed or None as we don't have all the txn's (portfolio level index is always tracked)

# For Debugging
def log_position_history(foo):
	log.info( "Position History ID: %d, Symbol: %s, Qty: %f, Val: %f, Index: %f" % (foo['positionId'], foo['symbol'], foo['quantity'], foo['value'], foo['index'] ) )

def log_position_history_by_id(id, positions_histories):
	if id in positions_histories:
		foo = positions_histories[id]
		log_position_history(foo)

def log_portfolio_txn(foo):
	if foo['portfolioAfter'] is not None:
		log.info( "Transaction: Type %d, Portfolio %d, Position %d, Val: %f, Index: %f, TCI %f" % (foo['type'], foo['portfolioId'], foo['positionId'], foo['value'], foo['portfolioAfter']['index'], foo['portfolioAfter']['totalCashInfusion']))
# Done

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + _datetime.timedelta(n)

def action_to_string(action):
	return "ID: %d Date: %s Type: %d" % (action.id, action.date.strftime("%Y-%m-%d"), action.actions_type_id)

def make_position_id_key(portfolio_id, symbol):
	return "%d:%s" % (portfolio_id, symbol)

def is_position_txn(db, txn):
	if txn['type'] in [db.CONST_BLB_TXN_TYPE_BUY, db.CONST_BLB_TXN_TYPE_SELL, db.CONST_BLB_TXN_TYPE_DIV]:
		return True
	return False

def convert_action(db, portfolio_id_map, position_id_map, action):
	ret = {
		'date': action.date.strftime("%Y-%m-%d"),
		'type': 0,
		'subType': 0,
		'positionId': 0,
		'portfolioId': 0,
		'value': 0,
		'quantity': 0,
		'positionBefore': {
			'symbol': action.symbol,
		},
		'note': "Backfilled, Togabou ID " + str(action.id),
	}
	if action.actions_type_id == db.CONST_ACTION_TYPE_INTEREST:
		ret['type'] = db.CONST_BLB_TXN_TYPE_INT
		ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_TOTAL
		ret['value'] = float(action.value1)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_DI:
		ret['type'] = db.CONST_BLB_TXN_TYPE_DI
		ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_TOTAL
		ret['value'] = float(action.value1)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_CI_PORTFOLIO:
		ret['type'] = db.CONST_BLB_TXN_TYPE_CI
		ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_PORTFOLIO
		ret['value'] = float(action.value1)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_CI_TOTAL:
		ret['type'] = db.CONST_BLB_TXN_TYPE_CI
		ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_TOTAL
		ret['value'] = float(action.value1)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_CI_PLAY:
		ret['type'] = db.CONST_BLB_TXN_TYPE_CI
		ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_SELFIE
		ret['value'] = float(action.value1)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_CI:
		ret['type'] = db.CONST_BLB_TXN_TYPE_CI
		ret['portfolioId'] = portfolio_id_map[int(action.value2)]
		ret['value'] = float(action.value1)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_DIVIDEND_PORTFOLIO:
		ret['type'] = db.CONST_BLB_TXN_TYPE_DIV
		ret['positionId'] = position_id_map[make_position_id_key(db.CONST_BLB_PORTFOLIO_PORTFOLIO, action.symbol)]
		ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_PORTFOLIO
		ret['value'] = float(action.value1)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_BOUGHT_MANAGED:
		ret['type'] = db.CONST_BLB_TXN_TYPE_CI
		ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_MANAGED
		ret['value'] = float(action.value1)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_DIVIDEND_TOTAL:
		ret['type'] = db.CONST_BLB_TXN_TYPE_INT
		ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_TOTAL
		ret['value'] = float(action.value1)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_BOUGHT_PORTFOLIO:
		ret['type'] = db.CONST_BLB_TXN_TYPE_BUY
		ret['positionId'] = position_id_map[make_position_id_key(db.CONST_BLB_PORTFOLIO_PORTFOLIO, action.symbol)]
		ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_PORTFOLIO
		ret['value'] = float(action.value1)
		ret['quantity'] = float(action.value2)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_SOLD_MANAGED:
		ret['type'] = db.CONST_BLB_TXN_TYPE_CI
		ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_MANAGED
		ret['value'] = -1*float(action.value1)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_SOLD_PORTFOLIO:
		ret['type'] = db.CONST_BLB_TXN_TYPE_SELL
		ret['positionId'] = position_id_map[make_position_id_key(db.CONST_BLB_PORTFOLIO_PORTFOLIO, action.symbol)]
		ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_PORTFOLIO
		ret['value'] = float(action.value1)
		ret['quantity'] = float(action.value2)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_DIVIDEND_PLAY:
		if action.symbol == 'CASH':
			ret['type'] = db.CONST_BLB_TXN_TYPE_INT
			ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_SELFIE
			ret['value'] = float(action.value1)			
		else:
			ret['type'] = db.CONST_BLB_TXN_TYPE_DIV
			ret['positionId'] = position_id_map[make_position_id_key(db.CONST_BLB_PORTFOLIO_SELFIE, action.symbol)]
			ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_SELFIE
			ret['value'] = float(action.value1)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_BOUGHT_PLAY:
		ret['type'] = db.CONST_BLB_TXN_TYPE_BUY
		ret['positionId'] = position_id_map[make_position_id_key(db.CONST_BLB_PORTFOLIO_SELFIE, action.symbol)]
		ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_SELFIE
		ret['value'] = float(action.value1)
		ret['quantity'] = float(action.value2)	
	elif action.actions_type_id == db.CONST_ACTION_TYPE_SOLD_PLAY:
		ret['type'] = db.CONST_BLB_TXN_TYPE_SELL
		ret['positionId'] = position_id_map[make_position_id_key(db.CONST_BLB_PORTFOLIO_SELFIE, action.symbol)]
		ret['portfolioId'] = db.CONST_BLB_PORTFOLIO_SELFIE
		ret['value'] = float(action.value1)
		ret['quantity'] = float(action.value2)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_DIVIDEND:
		portfolio_id = portfolio_id_map[int(action.value2)]
		if action.symbol == 'CASH':
			ret['type'] = db.CONST_BLB_TXN_TYPE_INT
			ret['portfolioId'] = portfolio_id
			ret['value'] = float(action.value1)			
		else:
			ret['type'] = db.CONST_BLB_TXN_TYPE_DIV
			ret['positionId'] = position_id_map[make_position_id_key(portfolio_id, action.symbol)]
			ret['portfolioId'] = portfolio_id
			ret['value'] = float(action.value1)
	elif action.actions_type_id == db.CONST_ACTION_TYPE_BOUGHT:
		portfolio_id = portfolio_id_map[int(action.value3)]
		ret['type'] = db.CONST_BLB_TXN_TYPE_BUY
		ret['positionId'] = position_id_map[make_position_id_key(portfolio_id, action.symbol)]
		ret['portfolioId'] = portfolio_id
		ret['value'] = float(action.value1)
		if action.value2 is not None:
			ret['quantity'] = float(action.value2)	
	elif action.actions_type_id == db.CONST_ACTION_TYPE_SOLD:
		portfolio_id = portfolio_id_map[int(action.value3)]
		ret['type'] = db.CONST_BLB_TXN_TYPE_SELL
		ret['positionId'] = position_id_map[make_position_id_key(portfolio_id, action.symbol)]
		ret['portfolioId'] = portfolio_id
		ret['value'] = float(action.value1)
		if action.value2 is not None:
			ret['quantity'] = float(action.value2)

	return ret

def default_portfolio_history(txn):
	return {
		'portfolioId': 0,
		'totalCashInfusion': 0,
		'divisor': 0,
		'index': 0,
		'value': 0,
	}

def default_position_history(txn):
	return {
		'portfolioId': 0,
		'positionId': 0,
		'symbol': "",
		'costBasis': 0,
		'totalCashInfusion': 0,
		'accumulatedDividends': 0,
		'divisor': 0,
		'index': 0,
		'value': 0,
		'quantity': 0,
		'pricingType': database2.CONST_PRICING_TYPE_BY_PRICE,
	}

def pre_prcosess_txn(db, txn, portfolios_histories, positions_histories):
	# Get the history objects or create defaults
	portfolio_history = default_portfolio_history(txn)
	if txn['portfolioId'] in portfolios_histories:
		portfolio_history = portfolios_histories[txn['portfolioId']]
	else:
		portfolio_history['portfolioId'] = txn['portfolioId']
		portfolios_histories[txn['portfolioId']] = portfolio_history
	position_history = default_position_history(txn)
	if txn['positionId'] in positions_histories:
		position_history = positions_histories[txn['positionId']]
	else:
		position_history['positionId'] = txn['positionId']
		position_history['symbol'] = txn['positionBefore']['symbol']
		positions_histories[txn['positionId']] = position_history

	# Deep copy before objects (need to flip id's)
	txn['portfolioBefore'] = deepcopy(portfolio_history)
	txn['portfolioBefore']['id'] = txn['portfolioBefore']['portfolioId']
	del txn['portfolioBefore']['portfolioId']
	if is_position_txn(db, txn):
		txn['positionBefore'] = deepcopy(position_history)
		txn['positionBefore']['id'] = txn['positionBefore']['positionId']
		del txn['positionBefore']['positionId']
	
	return portfolio_history, position_history

def process_txn(db, txn, portfolio_history, position_history):
	# Process the transaction
	if txn['type'] == db.CONST_BLB_TXN_TYPE_CI:
		portfolio_history['totalCashInfusion'] += txn['value']
		portfolio_history['value'] += txn['value']
	elif portfolio_history['portfolioId'] in CONST_TRACK_POS_INDEX:
		if txn['type'] == db.CONST_BLB_TXN_TYPE_BUY:
			position_history['totalCashInfusion'] += txn['value']
			position_history['costBasis'] += txn['value']
			if position_history['index'] <= 0:
				# Start index at 100 so we can easily check total pct gain
				position_history['index'] = 100.0
				position_history['divisor'] =  position_history['index'] / txn['value']
				position_history['value'] = txn['value']
				position_history['quantity'] = txn['quantity']
			else:
				position_history['value'] += txn['value']
				position_history['quantity'] += txn['quantity']
				position_history['divisor'] = position_history['index'] / position_history['value']
		elif txn['type'] == db.CONST_BLB_TXN_TYPE_SELL:
			position_history['totalCashInfusion'] -= txn['value']
			# Did we sell down to zero? Float qty's (VNE) caught us out, so compare the integer
			# Note: We don't handle CONST_PRICING_TYPE_BY_VALUE positions being sold down to zero,
			# but that's ok as we have not had any in the portfolios we track yet (so punt)
			if position_history['pricingType'] == db.CONST_PRICING_TYPE_BY_PRICE and int(txn['quantity']) == int(position_history['quantity']):
				position_history['costBasis'] = 0.0
				position_history['quantity'] = 0.0
				position_history['value'] = 0.0
				# Index is calculated one final time, and divisor is frozen at the final value
				position_history['index'] = txn['value'] * position_history['divisor']
				# There may be a sell after the last history row back when we had gaps, so force an update to the position table below in update_histories_and_currents
				position_history['forceUpdate'] = True
				log.info( "process_txn: %s (%d) sold to zero, index frozen at %f" % (txn['positionBefore']['symbol'],  position_history['positionId'], position_history['index']) )
			else:
				if position_history['pricingType'] == db.CONST_PRICING_TYPE_BY_PRICE:
					position_history['costBasis'] -= position_history['costBasis'] * (txn['quantity'] / position_history['quantity'])
				else:
					position_history['costBasis'] -= position_history['costBasis'] * (txn['value'] / position_history['value'])					
				position_history['value'] -= txn['value']
				position_history['quantity'] -= txn['quantity']
				position_history['divisor'] = position_history['index'] / position_history['value']
		elif txn['type'] == db.CONST_BLB_TXN_TYPE_DIV:
			position_history['accumulatedDividends'] += txn['value']
			# A dividend may come in after a position is sold down, we've decided to drop this for final index calculation, as there is no good way to handle it
			if position_history['value'] > 0.0:
				# Due to the dividend the index will increase, but then we basically immediately take the dividend out
				position_history['index'] = (position_history['value'] + txn['value']) * position_history['divisor']
				position_history['divisor'] = position_history['index'] / position_history['value']
	#elif txn['type'] == db.CONST_BLB_TXN_TYPE_DI: 	# Nothing needs updating for this migration, txn's are kept for audit purposes only
	#elif txn['type'] == db.CONST_BLB_TXN_TYPE_INT: # Nothing needs updating for this migration, txn's are kept for audit purposes only

def post_process_txn(db, txn, portfolio_history, position_history):
	# Deep copy after objects (need to flip id's)
	txn['portfolioAfter'] = deepcopy(portfolio_history)
	txn['portfolioAfter']['id'] = txn['portfolioAfter']['portfolioId']
	del txn['portfolioAfter']['portfolioId']
	if is_position_txn(db, txn):
		txn['positionAfter'] = deepcopy(position_history)
		txn['positionAfter']['id'] = txn['positionAfter']['positionId']
		del txn['positionAfter']['positionId']

def save_txn(txn):
	# Save the txn
	_abl.post_transaction(txn)

def	update_histories_and_currents(date, portfolios_histories, positions_histories):
	# Update any exisitng portfolio histories for today
	actual_portfolios_histories =_abl.portfolios_history_by_date(date)
	for actual_portfolio_history in actual_portfolios_histories:
		if actual_portfolio_history['portfolioId'] in portfolios_histories:
			portfolio_history = portfolios_histories[actual_portfolio_history['portfolioId']]
			actual_portfolio_history['totalCashInfusion'] = portfolio_history['totalCashInfusion']
			_abl.put_portfolios_history(actual_portfolio_history)

			# Update the current portfolio
			portfolio = _abl.portfolio_by_id(portfolio_history['portfolioId'])
			portfolio['totalCashInfusion'] = actual_portfolio_history['totalCashInfusion']
			_abl.put_portfolio(portfolio)
		
		# Save the existing portfolio history object for later use
		portfolios_histories[actual_portfolio_history['portfolioId']] = actual_portfolio_history

		# Update any exisitng position histories for today 
		actual_positions_histories =_abl.enriched_positions_history_by_portfolio_id_date(actual_portfolio_history['portfolioId'], date)
		for actual_position_history in actual_positions_histories:
			if actual_position_history['positionId'] in positions_histories:
				position_history = positions_histories[actual_position_history['positionId']]
				actual_position_history['costBasis'] = position_history['costBasis']
				actual_position_history['totalCashInfusion'] = position_history['totalCashInfusion']
				actual_position_history['accumulatedDividends'] = position_history['accumulatedDividends']
				actual_position_history['divisor'] = position_history['divisor']
				if int(position_history['value']) == 0 and position_history['index'] > 0.0:
					# If we've already sold down to zero, leave the index frozen to the last value (see CONST_BLB_TXN_TYPE_SELL handling above)
					actual_position_history['index'] = 	position_history['index']
					# Also, value and quantity should be zero (ZGNX is an example of value left around in Togabou position history after the final sell)
					actual_position_history['value'] = 	actual_position_history['quantity'] = 0.0
					log.info( "update_histories_and_currents: pos %d value zero, using index frozen at %f" % (actual_position_history['positionId'], position_history['index']) )
				else:
					# If the position is still live, calculate index with the latest history value 
					actual_position_history['index'] = actual_position_history['value'] * actual_position_history['divisor']
				_abl.put_positions_history(actual_position_history)

				# Update the current position
				position = _abl.position_by_id(actual_position_history['positionId'])
				position['costBasis'] = actual_position_history['costBasis']
				position['totalCashInfusion'] = actual_position_history['totalCashInfusion']
				position['accumulatedDividends'] = actual_position_history['accumulatedDividends']
				position['divisor'] = actual_position_history['divisor']
				position['index'] = actual_position_history['index']
				_abl.put_position(position)
				position_history.pop('forceUpdate', None) 
			
			# Save the existing position history object for later use
			positions_histories[actual_position_history['positionId']] = actual_position_history

		for position_history in positions_histories.values():
			if 'forceUpdate' in position_history:
				# We have sold down to zero, but there is not a position history row today. Update positions directly in case there is not another history row
				position = _abl.position_by_id(position_history['positionId'])
				position['costBasis'] = position_history['costBasis']
				position['totalCashInfusion'] = position_history['totalCashInfusion']
				position['accumulatedDividends'] = position_history['accumulatedDividends']
				position['divisor'] = position_history['divisor']
				position['index'] = position_history['index']
				position['quantity'] = position_history['quantity']
				position['value'] = position_history['value']
				_abl.put_position(position)
				position_history.pop('forceUpdate', None)

def main():
	log.info("Started...")

	db = database2()

	# Build up a portfolio id map and position id map
	portfolio_id_map = {
		db.CONST_PORTFOLIO_SELF: db.CONST_BLB_PORTFOLIO_PORTFOLIO,
        db.CONST_PORTFOLIO_MANAGED: db.CONST_BLB_PORTFOLIO_MANAGED,
        db.CONST_PORTFOLIO_NONE: db.CONST_BLB_PORTFOLIO_NONE,
        db.CONST_PORTFOLIO_PLAY: db.CONST_BLB_PORTFOLIO_SELFIE,
        db.CONST_PORTFOLIO_OAK: db.CONST_BLB_PORTFOLIO_OAK,
        db.CONST_PORTFOLIO_RISK_ARB: db.CONST_BLB_PORTFOLIO_RISK_ARB,
        db.CONST_PORTFOLIO_TRADE_FIN: db.CONST_BLB_PORTFOLIO_TRADE_FIN,
        db.CONST_PORTFOLIO_QUICK: db.CONST_BLB_PORTFOLIO_QUICK,
	}

	position_id_map = {}
	for portfolio_id in portfolio_id_map.values():
		positions = _abl.enriched_positions_all_by_portfolio_id(portfolio_id)
		for position in positions:
			position_id_map[make_position_id_key(portfolio_id, position['symbol'])] = position['id']

	# Get all Togabou actions
	actions = db.get_actions_all()
	action_index = 0

	# For debugging, catch up actions to CONST_START_DATE
	while action_index < len(actions):
		if actions[action_index].date < CONST_START_DATE:
			action_index += 1
			log.info("Skipping action at " + actions[action_index].date.strftime("%Y-%m-%d"))
		else:
			break

	log.info("Next action " + action_to_string(actions[action_index]))
	portfolios_histories = positions_histories = {}

	# For each day
	for raw_date in daterange(CONST_START_DATE, CONST_END_DATE):
		date = raw_date.strftime("%Y-%m-%d")
		log.info("Proccessing " + date)
		more_actions = True
		while more_actions == True:
			if action_index < len(actions) and actions[action_index].date.strftime("%Y-%m-%d") == date:
				# Convert Togabou action to Kapparu action
				log.info("Convert action")
				txn = convert_action(db, portfolio_id_map, position_id_map, actions[action_index])
				if txn is not None:
					# Process and save the Kapparu action
					portfolio_history, position_history = pre_prcosess_txn(db, txn, portfolios_histories, positions_histories)
					process_txn(db, txn, portfolio_history, position_history)
					post_process_txn(db, txn, portfolio_history, position_history)
					save_txn(txn)
				else:
					log.error("Proccessing " + date)
				action_index += 1
				if action_index < len(actions):
					log.info("Next action " + action_to_string(actions[action_index]))
			else:
				more_actions = False

		# Update Kapparu Portfolios, Positions, Portfolio Histories, Position Histories
		update_histories_and_currents(date, portfolios_histories, positions_histories)

	log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")