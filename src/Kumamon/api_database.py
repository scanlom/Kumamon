'''
Created on Aug 11, 2018

@author: scanlom

Uses the SQLAlchemy ORM to access the finances database
Notes
1.  Callers are exposed to ORM objects
2.  Callers do not access tables or SQLAlchemy objects directly
'''

from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from api_config import config_database2_connect
from api_log import log


class database2:
    CONST_DAYS_IN_YEAR = 365

    CONST_INDEX_SELF = 1
    CONST_INDEX_ROE = 2
    CONST_INDEX_ROTC = 3
    CONST_INDEX_MANAGED = 4
    CONST_INDEX_PLAY = 5
    CONST_INDEX_OAK = 23
    CONST_INDEX_RISK_ARB = 24
    CONST_INDEX_TRADE_FIN = 25
    CONST_INDEX_QUICK = 26

    CONST_PORTFOLIO_SELF = 1
    CONST_PORTFOLIO_MANAGED = 2
    CONST_PORTFOLIO_CASH = 3
    CONST_PORTFOLIO_NONE = 4
    CONST_PORTFOLIO_PLAY = 5
    CONST_PORTFOLIO_OAK = 23
    CONST_PORTFOLIO_RISK_ARB = 24
    CONST_PORTFOLIO_TRADE_FIN = 25
    CONST_PORTFOLIO_QUICK = 26

    CONST_BLB_PORTFOLIO_TOTAL = 1
    CONST_BLB_PORTFOLIO_SELFIE = 2
    CONST_BLB_PORTFOLIO_OAK = 3
    CONST_BLB_PORTFOLIO_MANAGED = 4
    CONST_BLB_PORTFOLIO_RISK_ARB = 5
    CONST_BLB_PORTFOLIO_TRADE_FIN = 6
    CONST_BLB_PORTFOLIO_QUICK = 7
    CONST_BLB_PORTFOLIO_PORTFOLIO = 8
    CONST_BLB_PORTFOLIO_NONE = 99

    CONST_BALANCES_TYPE_AMEX_CX = 1
    CONST_BALANCES_TYPE_CAPITAL_ONE = 2
    CONST_BALANCES_TYPE_HSBC = 3
    CONST_BALANCES_TYPE_HSBC_VISA = 4
    CONST_BALANCES_TYPE_VIRTUAL_BANK = 5
    CONST_BALANCES_TYPE_JPY = 6
    CONST_BALANCES_TYPE_OWE_PORTFOLIO = 7
    CONST_BALANCES_TYPE_ED = 8
    CONST_BALANCES_TYPE_GS = 9
    CONST_BALANCES_TYPE_GS_HKD = 10
    CONST_BALANCES_TYPE_GS_IRA = 11
    CONST_BALANCES_TYPE_TOTAL_ROE = 12
    CONST_BALANCES_TYPE_TOTAL_SELF = 13
    CONST_BALANCES_TYPE_TOTAL_MANAGED = 14
    CONST_BALANCES_TYPE_PAID = 15
    CONST_BALANCES_TYPE_TAX = 16
    CONST_BALANCES_TYPE_SAVINGS = 17
    CONST_BALANCES_TYPE_TOTAL_ROTC = 18
    CONST_BALANCES_TYPE_TOTAL_PLAY = 19
    CONST_BALANCES_TYPE_OAK = 23
    CONST_BALANCES_TYPE_RISK_ARB = 24
    CONST_BALANCES_TYPE_TRADE_FIN = 25
    CONST_BALANCES_TYPE_QUICK = 26

    CONST_PRICING_TYPE_BY_PRICE = 1
    CONST_PRICING_TYPE_BY_VALUE = 2

    CONST_SYMBOL_CASH = "CASH"
    CONST_SYMBOL_DEBT = "DEBT"

    CONST_ACTION_TYPE_BOUGHT_PORTFOLIO = 11
    CONST_ACTION_TYPE_SOLD_PORTFOLIO = 16
    CONST_ACTION_TYPE_DIVIDEND_PORTFOLIO = 1
    CONST_ACTION_TYPE_CI_TOTAL = 17

    def __init__(self):
        self.Base = automap_base()
        self.engine = create_engine(config_database2_connect)
        self.Base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine)
        self.Actions = self.Base.classes.actions
        self.Balances = self.Base.classes.balances
        self.BalancesHistory = self.Base.classes.balances_history
        self.Constituents = self.Base.classes.constituents
        self.Divisors = self.Base.classes.divisors
        self.DivisorsHistory = self.Base.classes.divisors_history
        self.Fundamentals = self.Base.classes.fundamentals
        self.IndexHistory = self.Base.classes.index_history
        self.PortfolioHistory = self.Base.classes.portfolio_history
        self.Researches = self.Base.classes.researches
        self.Spending = self.Base.classes.spending
        self.Stocks = self.Base.classes.stocks

    def commit(self):
        return self.session.commit()

    def get_constituents(self, pricing_type):
        return self.session.query(self.Constituents).filter(self.Constituents.pricing_type == pricing_type).all()

    def get_constituents_by_portfolio(self, portfolio):
        return self.session.query(self.Constituents).filter(self.Constituents.portfolio_id == portfolio).all()

    def get_constituents_by_portfolio_symbol(self, portfolio, symbol):
        return self.session.query(self.Constituents).filter(self.Constituents.portfolio_id == portfolio, self.Constituents.symbol == symbol).one().value

    def get_fundamentals(self, symbol, date):
        return self.session.query(self.Fundamentals).filter(self.Fundamentals.symbol == symbol, self.Fundamentals.date >= date).order_by(desc(self.Fundamentals.date)).all()

    def get_stocks(self):
        return self.session.query(self.Stocks).filter(self.Stocks.hidden == False).all()

    def get_stocks_all(self):
        return self.session.query(self.Stocks).all()

    def get_latest_research_by_symbol(self, symbol):
        return self.session.query(self.Researches).filter(self.Researches.symbol == symbol).order_by(self.Researches.date.desc()).first()

    def get_researches(self):
        return self.session.query(self.Researches).all()

    def get_balance(self, balance):
        return self.session.query(self.Balances).filter(self.Balances.type == balance).one().value

    def get_divisor(self, index):
        return self.session.query(self.Divisors).filter(self.Divisors.type == index).one().value

    def get_index(self, index):
        day = datetime.today()
        return self.session.query(self.IndexHistory).filter(self.IndexHistory.date == day, self.IndexHistory.type == index).one()

    def get_index_max(self, index):
        return self.session.query(func.max(self.IndexHistory.value)).filter(self.IndexHistory.type == index).scalar()

    def get_ytd_base_date(self):
        day = datetime.today()
        if day.month == 1 and day.day == 1:
            return date(day.year-1, 1, 1)
        return date(day.year, 1, 1)

    def get_qtd_base_date(self):
        day = datetime.today()
        if day.month > 9 and not (day.month == 10 and day.day == 1):
            return date(day.year, 10, 1)
        elif day.month > 6 and not (day.month == 7 and day.day == 1):
            return date(day.year, 7, 1)
        elif day.month > 3 and not (day.month == 4 and day.day == 1):
            return date(day.year, 4, 1)
        elif not (day.month == 1 and day.day == 1):
            return date(day.year, 1, 1)
        return date(day.year - 1, 10, 1)

    def get_day_base_date(self):
        yesterday = datetime.today() - timedelta(1)
        return date(yesterday.year, yesterday.month, yesterday.day)

    def get_balance_history(self, balance, date):
        row = self.session.query(self.BalancesHistory).filter(
            self.BalancesHistory.type == balance, self.BalancesHistory.date == date).one_or_none()
        ret = 0
        if row is not None:
            ret = row.value
        return ret

    def get_divisor_history(self, index, date):
        row = self.session.query(self.DivisorsHistory).filter(
            self.DivisorsHistory.type == index, self.DivisorsHistory.date == date).one_or_none()
        ret = 0
        if row is not None:
            ret = row.value
        return ret

    def get_index_history(self, index, date):
        return self.session.query(self.IndexHistory).filter(self.IndexHistory.type == index, self.IndexHistory.date == date).one().value

    def get_index_history_min_date(self, index):
        return self.session.query(func.min(self.IndexHistory.date)).filter(self.IndexHistory.type == index).scalar()

    def get_index_history_max_date(self, index):
        return self.session.query(func.max(self.IndexHistory.date)).filter(self.IndexHistory.type == index).scalar()

    def get_index_history_all(self, index):
        return self.session.query(self.IndexHistory).filter(self.IndexHistory.type == index).order_by(desc(self.IndexHistory.date)).all()

    def get_index_history_minus_years(self, index, years):
        date = datetime.now().date() - timedelta(days=years*database2.CONST_DAYS_IN_YEAR)
        date = self.session.query(func.max(self.IndexHistory.date)).filter(
            self.IndexHistory.type == index, self.IndexHistory.date <= date).scalar()
        return self.session.query(self.IndexHistory).filter(self.IndexHistory.type == index, self.IndexHistory.date == date).one()

    def get_index_history_minus_years_from_date(self, index, years, date):
        date = date - timedelta(days=years*database2.CONST_DAYS_IN_YEAR)
        date = self.session.query(func.max(self.IndexHistory.date)).filter(
            self.IndexHistory.type == index, self.IndexHistory.date <= date).scalar()
        return self.session.query(self.IndexHistory).filter(self.IndexHistory.type == index, self.IndexHistory.date == date).one()

    def get_portfolio_history(self, portfolio, symbol, date):
        return self.session.query(self.PortfolioHistory).filter(self.PortfolioHistory.type == portfolio, self.PortfolioHistory.symbol == symbol, self.PortfolioHistory.date == date).one().value

    def get_portfolio_history_safe(self, portfolio, symbol, date):
        row = self.session.query(self.PortfolioHistory).filter(self.PortfolioHistory.type == portfolio,
                                                               self.PortfolioHistory.symbol == symbol, self.PortfolioHistory.date == date).one_or_none()
        ret = 0
        if row is not None:
            ret = row.value
        return ret

    def get_portfolio_history_by_date(self, portfolio, date):
        return self.session.query(self.PortfolioHistory).filter(self.PortfolioHistory.type == portfolio, self.PortfolioHistory.date == date).all()

    def get_portfolio_history_all(self):
        return self.session.query(self.PortfolioHistory).order_by(desc(self.PortfolioHistory.date)).all()

    def get_actions_by_date_range_type(self, start, end, type):
        return self.session.query(self.Actions).filter(self.Actions.date >= start, self.Actions.date <= end, self.Actions.actions_type_id == type).all()

    def get_actions_by_type(self, type):
        return self.session.query(self.Actions).filter(self.Actions.actions_type_id == type).order_by(desc(self.Actions.date)).all()

    def get_ytd_spending_sum(self):
        ret = self.session.query(func.sum(self.Spending.amount)).filter(
            self.Spending.date >= self.get_ytd_base_date()).scalar()
        if ret == None:
            return Decimal(0.0)
        return ret

    def get_ytd_spending_sum_by_date(self, date):
        ret = self.session.query(func.sum(self.Spending.amount)).filter(
            self.Spending.date >= self.get_ytd_base_date(), self.Spending.date <= date).scalar()
        if ret == None:
            return Decimal(0.0)
        return ret

    def get_ytd_spending_sum_by_types(self, types):
        ret = self.session.query(func.sum(self.Spending.amount)).filter(
            self.Spending.date >= self.get_ytd_base_date(), self.Spending.type.in_(types)).scalar()
        if ret == None:
            return Decimal(0.0)
        return ret

    def get_ytd_spendings_by_types(self, types, minimum):
        return self.session.query(self.Spending).filter(self.Spending.date >= self.get_ytd_base_date(),
                                                        self.Spending.type.in_(
                                                            types),
                                                        self.Spending.amount >= minimum).order_by(desc(self.Spending.date)).all()


def main():
    log.info("Started...")

    # Test
    db = database2()
    val = db.get_balance(database2.CONST_BALANCES_TYPE_TOTAL_ROE)
    print(val)
    print(db.get_ytd_base_date())
    db.session.query(db.IndexHistory).filter(
        db.IndexHistory.type == 2, db.IndexHistory.date == '08/14/2018').one()
    print(db.get_ytd_spending_sum([0, 2, 3, 4, 5, 8, 12, 96]))
    print(db.get_stocks())

    log.info("Completed")


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
