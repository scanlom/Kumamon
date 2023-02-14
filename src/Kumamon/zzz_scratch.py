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
		'date': '2023-02-11',
		'type': database2.CONST_BLB_TXN_TYPE_CI,
		'subType': 0,
		'positionId': 0,
		'portfolioId': 7,
		'value': -72.37,
		'quantity': 0,
		'note': "",
	}
    _abl.execute_book_transaction(ret)

    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 