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
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from api_config import config_database2_connect
from api_log import log

class database2:
    CONST_DAYS_IN_YEAR      = 365
    
    CONST_INDEX_PORTFOLIO   = 1
    CONST_INDEX_ROE         = 2
    CONST_INDEX_ROTC        = 3
    CONST_INDEX_MANAGED     = 4
    CONST_INDEX_PLAY        = 5
    
    CONST_BALANCES_TYPE_TOTAL_ROE       = 12
    CONST_BALANCES_TYPE_TOTAL_SELF      = 13
    CONST_BALANCES_TYPE_TOTAL_MANAGED   = 14
    CONST_BALANCES_TYPE_PAID            = 15
    CONST_BALANCES_TYPE_TAX             = 16
    CONST_BALANCES_TYPE_SAVINGS         = 17
    CONST_BALANCES_TYPE_TOTAL_ROTC      = 18
    CONST_BALANCES_TYPE_TOTAL_PLAY      = 19
    
    CONST_PRICING_TYPE_BY_PRICE = 1
    
    def __init__(self):
        self.Base = automap_base()
        self.engine = create_engine(config_database2_connect)
        self.Base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine)
        self.Balances = self.Base.classes.balances
        self.BalancesHistory = self.Base.classes.balances_history
        self.Constituents = self.Base.classes.constituents
        self.IndexHistory = self.Base.classes.index_history
        self.Spending = self.Base.classes.spending
        self.Stocks = self.Base.classes.stocks
        
    def commit(self):
        return self.session.commit()

    def get_constituents(self, pricing_type):
        return self.session.query(self.Constituents).filter(self.Constituents.pricing_type == pricing_type).all()
    
    def get_stocks(self):
        return self.session.query(self.Stocks).all()
    
    def get_balance(self, balance):
        return self.session.query(self.Balances).filter(self.Balances.type == balance).one().value
    
    def get_ytd_base_date(self):
        day = datetime.today()
        if day.month == 1 and day.day == 1:
            return date(day.year-1,1,1)
        return date(day.year,1,1)

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
        day = datetime.today()
        return date(day.year, day.month, day.day - 1)
    
    def get_balance_history(self, balance, date):
        return self.session.query(self.BalancesHistory).filter(self.BalancesHistory.type == balance, self.BalancesHistory.date == date).one().value
       
    def get_index_history(self, index, date):
        return self.session.query(self.IndexHistory).filter(self.IndexHistory.type == index, self.IndexHistory.date == date).one().value
    
    def get_index_history_minus_years(self, index, years):
        date = datetime.now().date() - timedelta(days=years*database2.CONST_DAYS_IN_YEAR)
        date = self.session.query(func.max(self.IndexHistory.date)).filter(self.IndexHistory.type == index, self.IndexHistory.date <= date).scalar()
        return self.session.query(self.IndexHistory).filter(self.IndexHistory.type == index, self.IndexHistory.date == date).one()
    
    def get_ytd_spending_sum(self, types):
        return self.session.query(func.sum(self.Spending.amount)).filter(self.Spending.date >= self.get_ytd_base_date(), self.Spending.type.in_(types)).scalar()

def main():
    log.info("Started...")
    
    # Test
    db = database2()
    val = db.get_balance(database2.CONST_BALANCES_TYPE_TOTAL_ROE)
    print(val)
    print(db.get_ytd_base_date())
    db.session.query(db.IndexHistory).filter(db.IndexHistory.type == 2, db.IndexHistory.date == '08/14/2018').one()
    print(db.get_ytd_spending_sum([ 0,2,3,4,5,8,12,96 ]))
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 