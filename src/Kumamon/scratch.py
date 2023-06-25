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
		'date': '2023-06-06',
		'type': database2.CONST_BLB_TXN_TYPE_BUY,
		'subType': 0,
		'positionId': 311,
		'portfolioId': 5,
		'value': 4204.8,
		'quantity': 1000,
		'note': '',
#		'note': 'AMED 15DEC23 100 C',
	}
    _abl.execute_book_transaction(ret)

    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 