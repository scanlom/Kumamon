'''
Created on Aug 7, 2013
@author: scanlom
'''

from lib_mail import send_mail_html_self
from lib_reporting import report
from api_analytics import historicals
from lib_constants import CONST
from lib_log import log
from api_blue_lion import ref_data_focus, mdh_by_ref_data_id_date, post_market_data_historical, put_market_data_historical

def main():
    log.info("Started loading market data...")
    instruments = ref_data_focus()
    ref_data_msg = ""

    #instruments = [{
    #    'id': 3303,
    #    'symbol': '8074.T',
    #    'symbolAlphaVantage': '8074.T',
    #}]

    for i in instruments:
        try:
            h = historicals( i['symbolAlphaVantage'] )
        except Exception as err:
            msg = "Could not get data for %s<br>" % ( i['symbol'] )
            log.warning( msg )
            ref_data_msg += msg
            continue   
        log.info("Populating for %s" % (i['symbol']))
        post = 0
        put = 0
        for close, adj_close in zip(h.data_close, h.data_adj_close):
            if close[0] != adj_close[0]:
                raise RuntimeError('Date mismatch: close: %s, adj_close: %s' % (close[0], adj_close[0]))
            mdh = mdh_by_ref_data_id_date(i['id'],close[0])
            if mdh == None:
                post_market_data_historical( close[0], i['id'], close[1], adj_close[1] )
                post += 1
            else:   
                put_market_data_historical( mdh['id'], close[0], i['id'], close[1], adj_close[1] )
                put += 1
        log.info("Posted %d records, Put %d records" % (post, put))

    rpt = report()
    rpt.add_string( ref_data_msg )
    subject = 'Blue Lion - Market Data Historical Update - Bad Ref Data'
    send_mail_html_self(subject, rpt.get_html())

    log.info("Completed")
    
if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")