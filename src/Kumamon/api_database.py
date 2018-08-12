'''
Created on Aug 11, 2018

@author: scanlom
'''
from datetime import datetime
from datetime import timedelta
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from log import log

class database2:
    CONST_DAYS_IN_YEAR      = 365
    
    CONST_INDEX_PORTFOLIO   = 1
    CONST_INDEX_ROE         = 2
    CONST_IDNEX_ROTC        = 3
    CONST_INDEX_MANAGED     = 4
    CONST_INDEX_PLAY        = 5
    
    def __init__(self):
        self.Base = automap_base()
        self.engine = create_engine('postgresql://scanlom:buck123@localhost/finances')
        self.Base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine)
        self.IndexHistory = self.Base.classes.index_history
        
    def get_index_row_minus_years(self, index, years):
        date = datetime.now() - timedelta(days=years*database2.CONST_DAYS_IN_YEAR)
        date = self.session.query(func.max(self.IndexHistory.date)).filter(self.IndexHistory.type == index, self.IndexHistory.date <= date).scalar()
        return self.session.query(self.IndexHistory).filter(self.IndexHistory.type == index, self.IndexHistory.date == date).one();

def main():
    log.info("Started...")
    
    # Test
    db = database2()
    row = db.get_index_row_minus_years(database2.CONST_INDEX_ROE, 12)
    print(row.date)
    print(row.value)
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 