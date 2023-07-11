'''
Created on Jul 27, 2013
@author: scanlom

Downloads account information using ofxclient
'''

from os import path
from ofxtools.Client import OFXClient, InvStmtRq
from ofxtools.Parser import OFXTree
import api_blue_lion as _abl
from lib_config import config_ofx_symbols, config_ofx_user1, config_ofx_pass1, config_ofx_acct1, config_ofx_user2, config_ofx_pass2, config_ofx_acct2 
from lib_constants import CONST
from lib_log import log

def main():
    log.info("Started...")

    symbols = config_ofx_symbols

    client = OFXClient("https://vesnc.vanguard.com/us/OfxProfileServlet", userid=config_ofx_user1,
                    org="Vanguard", fid="15103", brokerid="vanguard.com", prettyprint=True,
                    version=220)

    response = client.request_statements(config_ofx_pass1, InvStmtRq(acctid=config_ofx_acct1) )
    parser = OFXTree()
    parser.parse(response)
    ofx = parser.convert()
    for pos in ofx.invstmtmsgsrsv1[0].invstmtrs.invposlist:
        if pos.mktval > 0 and pos.secid.uniqueid in symbols:
            kpos = _abl.positions_by_symbol_portfolio_id(symbols[pos.secid.uniqueid], CONST.PORTFOLIO_MANAGED)
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
            kpos = _abl.positions_by_symbol_portfolio_id(symbols[pos.secid.uniqueid], db.CONST_BLB_PORTFOLIO_MANAGED)
            kpos['value'] = float( pos.mktval )
            _abl.put_position(kpos)
            log.info("Kapparu Set: " + str(kpos['refDataId']) + " to " + str(kpos['value']))
        elif pos.mktval > 0:
            log.info("Unprocessed: " + pos.secid.uniqueid + " with value " + str(pos.mktval))
                       
    log.info("Completed")
            
if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        log.exception(err)
        log.error("Aborted")