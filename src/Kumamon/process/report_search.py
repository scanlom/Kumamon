'''
Created on Dec 8, 2019
@author: scanlom
'''

from decimal import Decimal
from lib_log import log
from lib_mail import send_mail_html_self
from lib_reporting import report
import api_blue_lion as _abl

CONST_CONFIDENCE_NONE           = 'NONE'
CONST_CONFIDENCE_HIGH           = 'HIGH'
CONST_CONFIDENCE_MEDIUM         = 'MEDIUM'
CONST_CONFIDENCE_BLAH           = 'BLAH'
CONST_CONFIDENCE_LOW            = 'LOW'
CONST_CONFIDENCE_CONSTITUENT    = 'CONSTITUENT'

def expand_confidence(c):
    if c == 'H':
        return CONST_CONFIDENCE_HIGH
    if c == 'M':
        return CONST_CONFIDENCE_MEDIUM
    if c == 'N':
        return CONST_CONFIDENCE_NONE
    if c == 'B':
        return CONST_CONFIDENCE_BLAH
    if c == 'L':
        return CONST_CONFIDENCE_LOW

def populate_five_cagr( rpt ):
    log.info("Populate_five_cagr called...")
    rows = _abl.projections_positions()
    rows += _abl.projections_watch()
    rows += _abl.projections_research()
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_PCT_COLOR, rpt.CONST_FORMAT_CONFIDENCE ]
    table = [ ]
    for row in rows:
        if row['cagr5yr'] > Decimal(0.10):
            c = expand_confidence(row['confidence'])
            if row['percentPortfolio'] > Decimal(0.0):
                c = CONST_CONFIDENCE_CONSTITUENT
            if c != CONST_CONFIDENCE_LOW and c != CONST_CONFIDENCE_BLAH:
                table.append( [ row['ticker'], row['cagr5yr'], c ] )
    if len(table) > 1:
        table.sort(key=lambda a : a[1],reverse=True)
        table.insert(0, [ "Symbol", "5yr CAGR", "Confidence" ])
        rpt.add_heading( "Watch List - 5yr CAGR > 10%" )
        rpt.add_table( table, formats )
    else:
        rpt.add_heading( "Watch List - 5yr CAGR > 10% - None" )

def populate_magic( rpt ):
    log.info("Populate_magic called...")
    rpt.add_heading( "Screen - Magic Top Ten - Magic = CAGR5yr where NetMgn >= 10%%, LTDRatio <= 3.5, EPS > 0.0 last five years" )
    projections = []
    rows = _abl.projections_positions()
    rows += _abl.projections_watch()
    rows += _abl.projections_research()
    instruments = _abl.ref_data()
    # Remove duplicates
    remove_symbols = [i['ticker'] for i in rows]
    instruments = [i for i in instruments if i['symbol'] not in remove_symbols]
    for i in instruments:
        log.info("Requesting projections for " + i['symbol'])
        projections.append(_abl.projections_by_symbol( i['symbol'] ))
    sorted_projections = sorted(projections, reverse = True, key = lambda i: i['magic'])
    formats = [ rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_NONE, rpt.CONST_FORMAT_CCY_COLOR ]
    table = [ ]
    table.append( [ "Ticker", "Description", "Magic" ] )
    for x in range(10):
        table.append( [sorted_projections[x]['ticker'], sorted_projections[x]['description'], sorted_projections[x]['magic']] )
    rpt.add_table( table, formats )

def main():
    log.info("Started...")
    rpt = report()
    
    populate_five_cagr( rpt )
    populate_magic( rpt )
  
    subject = 'Blue Lion - Search'
    send_mail_html_self(subject, rpt.get_html())
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")