'''
Created on Jul 27, 2013

Downloads account information using ofxclient

@author: scanlom
'''

from os import path
from ofxtools.Client import OFXClient, InvStmtRq
from ofxtools.Parser import OFXTree
from psycopg2 import connect
from psycopg2.extras import DictCursor       
from api_config import config_database_connect, config_ofx_symbols, config_ofx_user1, config_ofx_pass1, config_ofx_acct1, config_ofx_user2, config_ofx_pass2, config_ofx_acct2 
from api_database import database2
from api_log import log
import api_blue_lion as _abl

def main():
    log.info("Started...")

    symbols = config_ofx_symbols
    
    # Connect to the db
    conn = connect( config_database_connect )
    cur = conn.cursor(cursor_factory=DictCursor)
    db = database2()

    client = OFXClient("https://vesnc.vanguard.com/us/OfxProfileServlet", userid=config_ofx_user1,
                    org="Vanguard", fid="15103", brokerid="vanguard.com", prettyprint=True,
                    version=220)

    response = client.request_statements(config_ofx_pass1, InvStmtRq(acctid=config_ofx_acct1) )
    parser = OFXTree()
    parser.parse(response)
    ofx = parser.convert()
    for pos in ofx.invstmtmsgsrsv1[0].invstmtrs.invposlist:
        if pos.mktval > 0 and pos.secid.uniqueid in symbols:
            sql = "update constituents set value=" + str(pos.mktval) + " where symbol='" + symbols[pos.secid.uniqueid] + "'"
            cur.execute(sql)
            conn.commit()
            log.info("Togabou Set: " + symbols[pos.secid.uniqueid] + " to " + str(pos.mktval))
            kpos = _abl.positions_by_symbol_portfolio_id(symbols[pos.secid.uniqueid], db.CONST_BLB_PORTFOLIO_MANAGED)
            kpos['value'] = float( pos.mktval )
            _abl.put_position(kpos)
            log.info("Kapparu Set: " + str(kpos['refDataId']) + " to " + str(kpos['value']))

        elif pos.mktval > 0:
            log.info("Unprocessed: " + pos.secid.uniqueid + " with value " + str(pos.mktval))
    
    client = OFXClient("https://seven.was.alight.com/eftxweb/access.ofx", userid=config_ofx_user2,
                    org="hewitt.com", fid="242", brokerid="hewitt.com", prettyprint=True,
                    version=220)

    response = client.request_statements(config_ofx_pass2, InvStmtRq(acctid=config_ofx_acct2))
    parser = OFXTree()
    parser.parse(response)
    ofx = parser.convert()
    for pos in ofx.invstmtmsgsrsv1[0].invstmtrs.invposlist:
        if pos.mktval > 0 and pos.secid.uniqueid in symbols:
            sql = "update constituents set value=" + str(pos.mktval) + " where symbol='" + symbols[pos.secid.uniqueid] + "'"
            cur.execute(sql)
            conn.commit()
            log.info("Togabou Set: " + symbols[pos.secid.uniqueid] + " to " + str(pos.mktval))
            kpos = _abl.positions_by_symbol_portfolio_id(symbols[pos.secid.uniqueid], db.CONST_BLB_PORTFOLIO_MANAGED)
            kpos['value'] = float( pos.mktval )
            _abl.put_position(kpos)
            log.info("Kapparu Set: " + str(kpos['refDataId']) + " to " + str(kpos['value']))
        elif pos.mktval > 0:
            log.info("Unprocessed: " + pos.secid.uniqueid + " with value " + str(pos.mktval))
                       
    # Close the db
    cur.close()
    conn.close()
    log.info("Completed")
            
if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        log.exception(err)
        log.error("Aborted")