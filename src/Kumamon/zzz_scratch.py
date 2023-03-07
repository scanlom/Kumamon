'''
Created on February 2, 2023

@author: scanlom
'''

from datetime import datetime
from yahooquery import Ticker
import api_blue_lion as _abl
from api_database import database2
from api_log import log

def main():
    log.info("Started...")
    
    """ret = {
		'date': '2023-02-27',
		'type': database2.CONST_BLB_TXN_TYPE_DIV,
		'subType': 1,
		'positionId': 268,
		'portfolioId': 5,
		'value': 111.59,
		'quantity': 0,
		'note': "ATVI 21APR23 90 C",
	}
    _abl.execute_book_transaction(ret)"""

    

    aapl = Ticker('aapl')

    foo = aapl.price['aapl']['regularMarketPrice']
    print(foo)

    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 