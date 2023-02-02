'''
Created on February 2, 2023

@author: scanlom
'''

from datetime import datetime
import api_blue_lion as _abl
from api_database import database2
from api_log import log

def main():
    log.info("Started...")
    
    ret = {
		'date': '2023-01-31',
		'type': database2.CONST_BLB_TXN_TYPE_DIV,
		'subType': 1,
		'positionId': 268,
		'portfolioId': 5,
		'value': 58.65,
		'quantity': 0,
		'note': "ATVI 17FEB23 85 C",
	}
    _abl.execute_book_transaction(ret)

    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 