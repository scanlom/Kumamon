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
    for row in rows:
        log.info("Processing %s %d %s" % (row.date, row.type, row.symbol))
        if row.type == db.CONST_PORTFOLIO_CASH:
            # Cash portfolio is handled by portfolios backfill
            continue
        if row.symbol == db.CONST_SYMBOL_CASH:
            # Cash symbol is handled by portfolios backfill
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
            data['id'] = position['id']
            _abl.put_position(data)
            del data['id']
        data['date'] = row.date.strftime('%Y-%m-%d')
        data['positionId'] = position['id']
        _abl.post_positions_history(data)

    log.info("Completed")


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
