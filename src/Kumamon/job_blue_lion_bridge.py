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
    rows = db.get_researches()
    f = open("tmp.txt", "w")
    
    for r in rows:
        p = _abl.projections_by_symbol(r.symbol)
        ref = _abl.ref_data_by_symbol(r.symbol)
        if p is None or p['id'] == 0:
            print("No projections found for " + r.symbol)
            continue # will handle manually
        confidence = _abl.confidence(r.comment)[0]
        eps_yr1 = r.eps_yr1 if r.eps_yr1 is not None else 0
        eps_yr2 = r.eps_yr2 if r.eps_yr2 is not None else 0
        comment = r.comment.replace("'", "''")

        f.write("""INSERT INTO public.projections_journal(
        projections_id, ref_data_id, date, eps, dps, growth, pe_terminal, payout, book, roe, eps_yr1, eps_yr2, confidence, ticker, description, 
        sector, industry, price, div_plus_growth, eps_yield, dps_yield, cagr_5yr, cagr_10yr, croe_5yr, croe_10yr, entry, eps_cagr_5yr, eps_cagr_10yr, pe_high_mmo_5yr, pe_low_mmo_5yr, roe_5yr, pe, eps_cagr_2yr, eps_cagr_7yr, magic)
        VALUES (%d, %d, '%s', %f, %f, %f, %d, %f, %f, %f, %f, %f, '%s', '%s', '%s', '%s', '%s', %f, %f, %f, %f, %f, %f, %f, %f, '%s',0,0,0,0,0,0,0,0,0);\n""" % (p['id'], ref['id'], r.date.strftime('%Y-%m-%d'), r.eps, r.div, r.growth, r.pe_terminal, r.payout, r.book, r.roe, eps_yr1, eps_yr2, confidence, ref['symbol'], ref['description'], ref['sector'], ref['industry'], r.price, r.div_plus_growth, r.eps_yield, r.div_yield, r.five_year_cagr, r.ten_year_cagr, r.five_year_croe, r.ten_year_croe, comment) )

    f.close()
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")