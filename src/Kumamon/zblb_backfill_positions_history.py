'''
Created on Jan 27, 2022

@author: scanlom
'''

'''
Summary:
Togabou -> Fujippi Migration. Backfills Togabou positions history to Fujippi. Note that
index, divisor, totalCashInfusion, costBasis, and accumulatedDividends values are left blank
to be populated by the transactions script

Togabou Touchpoints:
db.get_portfolio_history_all

Sanomaru Touchpoints:
_abl.portfolios_history_by_portfolio_id_date
_abl.post_portfolios_history
_abl.ref_data_by_symbol
_abl.positions_by_symbol_portfolio_id
_abl.put_position
_abl.post_positions_history

Prep:
1. Ensure portfolios_history is up to date
2. Run:
delete from positions_history;
ALTER SEQUENCE positions_history_id_seq RESTART WITH 1;
'''

from api_database import database2
import api_blue_lion as _abl
from api_log import log

def map_blb_portfolio_id(db, id):
    mapIDs = {
        db.CONST_PORTFOLIO_SELF: db.CONST_BLB_PORTFOLIO_PORTFOLIO,
        db.CONST_PORTFOLIO_MANAGED: db.CONST_BLB_PORTFOLIO_MANAGED,
        db.CONST_PORTFOLIO_NONE: db.CONST_BLB_PORTFOLIO_NONE,
        db.CONST_PORTFOLIO_PLAY: db.CONST_BLB_PORTFOLIO_SELFIE,
        db.CONST_PORTFOLIO_OAK: db.CONST_BLB_PORTFOLIO_OAK,
        db.CONST_PORTFOLIO_RISK_ARB: db.CONST_BLB_PORTFOLIO_RISK_ARB,
        db.CONST_PORTFOLIO_TRADE_FIN: db.CONST_BLB_PORTFOLIO_TRADE_FIN,
        db.CONST_PORTFOLIO_QUICK: db.CONST_BLB_PORTFOLIO_QUICK,
    }

    if id in mapIDs:
        return mapIDs[id]
    log.info("Failed to map portfolio id " + str(id))
    raise LookupError()

def main():
    log.info("Started...")

    db = database2()
    rows = db.get_portfolio_history_all()
    rows_processed = rows_portfolio_cash = rows_symbol_cash = rows_position_added = rows_history_added = 0
    for row in rows:
        log.info("Processing %s %d %s" % (row.date, row.type, row.symbol))
        rows_processed += 1
        if row.type == db.CONST_PORTFOLIO_CASH:
            # Cash portfolio is handled by portfolios backfill
            rows_portfolio_cash += 1
            continue
        if row.symbol == db.CONST_SYMBOL_CASH:
            # Cash symbol is handled by portfolios backfill
            rows_symbol_cash += 1
            continue
        if row.type == db.CONST_PORTFOLIO_NONE:
            # None portfolio we should add ourselves if necessary
            portfolio_history = _abl.portfolios_history_by_portfolio_id_date(
                db.CONST_BLB_PORTFOLIO_NONE, row.date)
            if portfolio_history is None:
                _abl.post_portfolios_history({
                    'date': row.date.strftime('%Y-%m-%d'),
                    'portfolioId': db.CONST_BLB_PORTFOLIO_NONE,
                    'name': 'None',
                    'value': 0,
                    'active': True,
                    'index': 0,
                    'divisor': 0,
                    'cash': 0,
                    'debt': 0,
                    'valueTotalCapital': 0,
                    'indexTotalCapital': 0,
                    'divisorTotalCapital': 0,
                    'costBasis': 0,
                })
        blb_portfolio_id = map_blb_portfolio_id(db, row.type)
        blb_ref_data = _abl.ref_data_by_symbol(row.symbol)

        data = {
            'refDataId': blb_ref_data['id'],
            'portfolioId': blb_portfolio_id,
            'quantity': row.quantity,
            'price': row.price,
            'value': row.value,
            'index': 0,
            'divisor': 0,
            'costBasis': 0,
            'model': 0,
            'pricingType': row.pricing_type,
        }

        position = _abl.positions_by_symbol_portfolio_id(row.symbol, blb_portfolio_id)
        if position is None:
            # If the position is not present, add it, but it must be non active if it doesn't have a record yet
            data['active'] = False
            _abl.post_position(data)
            # Get the position again so we have the correct id
            position = _abl.positions_by_symbol_portfolio_id(row.symbol, blb_portfolio_id)
        else:
            # Update the position with current data (records are sorted by date so our final update will the one kept)
            data['active'] = position['active']
            data['model'] = position['model']
            data['id'] = position['id']
            _abl.put_position(data)
            del data['id']
        data['date'] = row.date.strftime('%Y-%m-%d')
        data['positionId'] = position['id']
        data['active'] = True # Position would have been active at the point history was snapped
        data['model'] = 0.0 # There was no tracking of model history under Togabou
        _abl.post_positions_history(data)
        rows_history_added += 1

    log.info("%d rows_processed %d rows_portfolio_cash %d rows_symbol_cash %d rows_position_added %d rows_history_added" % (rows_processed, rows_portfolio_cash, rows_symbol_cash, rows_position_added, rows_history_added))
    log.info("Completed")


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
