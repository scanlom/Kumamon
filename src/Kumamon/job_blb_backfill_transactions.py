'''
Created on Jan 27, 2022

@author: scanlom
'''

import datetime as _datetime
import json as _json
from api_database import database2
import api_blue_lion as _abl
import api_fundamentals as _af
from api_log import log

def main():
	log.info("Started...")

	db = database2()    
	rows = db.get_actions_by_type(db.CONST_ACTION_TYPE_CI_TOTAL)
	total_ci = 0
	for row in rows:
		total_ci += row.value1
	print(total_ci)

	log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")