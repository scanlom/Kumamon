'''
Created on February 2, 2023
@author: scanlom
'''

import api_blue_lion as _abl
from api_database import database2
from lib_log import log

def main():
    log.info("Started...")
    
    ret = {
		'date': '2023-07-10',
		'type': database2.CONST_BLB_TXN_TYPE_CI,
		'subType': 0,
		'positionId': 0,
		'portfolioId': 4,
		'value': -1510.80,
		'quantity': 0,
		'note': '',
#		'note': 'ABBV 28JUL23 120 P',
	}
    _abl.execute_book_transaction(ret)

    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 