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
    rows = db.get_stocks_all()
    for r in rows:
        ref_data_id = _abl.ref_data_by_symbol(r.symbol)['id']
        research = db.get_latest_research_by_symbol(r.symbol)
        confidence = 'N'
        date = r.created_at
        eps_yr1 = 0
        eps_yr2 = 0
        if research is not None:
            confidence = _abl.confidence(research.comment)[0]
            date = research.date
            eps_yr1 = research.eps_yr1 if research.eps_yr1 is not None else 0
            eps_yr2 = research.eps_yr2 if research.eps_yr2 is not None else 0
            
        
        print( """INSERT INTO public.projections(ref_data_id, date, eps, dps, growth, pe_terminal, payout, book, roe, eps_yr1, eps_yr2, confidence)	
        VALUES (%d, '%s', %f, %f, %f, %d, %f, %f, %f, %f, %f, '%s');""" % (ref_data_id, date.strftime("%Y-%m-%d"), r.eps, r.div, r.growth, r.pe_terminal, r.payout, r.book, r.roe, eps_yr1, eps_yr2, confidence) )

    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")