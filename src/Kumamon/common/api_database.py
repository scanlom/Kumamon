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
from decimal import Decimal
from sqlalchemy import asc, create_engine
from sqlalchemy import desc
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from lib_common import get_ytd_base_date
from lib_config import config_database2_connect
from lib_log import log


class database2:

    def __init__(self):
        self.Base = automap_base()
        self.engine = create_engine(config_database2_connect)
        self.Base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine)
        self.Spending = self.Base.classes.spending

    def get_ytd_spending_sum(self):
        ret = self.session.query(func.sum(self.Spending.amount)).filter(
            self.Spending.date >= get_ytd_base_date()).scalar()
        if ret == None:
            return Decimal(0.0)
        return ret

    def get_ytd_spending_sum_by_types(self, types):
        ret = self.session.query(func.sum(self.Spending.amount)).filter(
            self.Spending.date >= get_ytd_base_date(), self.Spending.type.in_(types)).scalar()
        if ret == None:
            return Decimal(0.0)
        return ret

    def get_ytd_spendings_by_types(self, types, minimum):
        return self.session.query(self.Spending).filter(self.Spending.date >= get_ytd_base_date(),
                                                        self.Spending.type.in_(
                                                            types),
                                                        self.Spending.amount >= minimum).order_by(desc(self.Spending.date)).all()


def main():
    log.info("Started...")

    # Test
    db = database2()
    print(db.get_ytd_spending_sum_by_types([0, 2, 3, 4, 5, 8, 12, 96]))

    log.info("Completed")


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
