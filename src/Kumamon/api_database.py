'''
Created on Aug 11, 2018

@author: scanlom

Uses the SQLAlchemy ORM to access the finances database
Notes
1.  Callers are exposed to ORM objects
2.  Callers do not access tables or SQLAlchemy objects directly
'''
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
    CONST_IDNEX_ROTC        = 3
    CONST_INDEX_MANAGED     = 4
    CONST_INDEX_PLAY        = 5
    
    CONST_PRICING_TYPE_BY_PRICE = 1
    
    def __init__(self):
        self.Base = automap_base()
        self.engine = create_engine(config_database2_connect)
        self.Base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine)
        self.IndexHistory = self.Base.classes.index_history
        self.Constituents = self.Base.classes.constituents
        self.Stocks = self.Base.classes.stocks
        
    def commit(self):
        return self.session.commit()
    
    def get_index_row_minus_years(self, index, years):
        date = datetime.now() - timedelta(days=years*database2.CONST_DAYS_IN_YEAR)
        date = self.session.query(func.max(self.IndexHistory.date)).filter(self.IndexHistory.type == index, self.IndexHistory.date <= date).scalar()
        return self.session.query(self.IndexHistory).filter(self.IndexHistory.type == index, self.IndexHistory.date == date).one()

    def get_constituents(self, pricing_type):
        return self.session.query(self.Constituents).filter(self.Constituents.pricing_type == pricing_type).all()
    
    def get_stocks(self):
        return self.session.query(self.Stocks).all()

def main():
    log.info("Started...")
    
    # Test
    db = database2()
    rows = db.get_constituents(database2.CONST_PRICING_TYPE_BY_PRICE)
    print(rows[0].symbol)
    
    rows = db.get_stocks()
    print(rows[0].symbol)
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 