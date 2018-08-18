'''
Created on Jul 27, 2013

Downloads account information using ofxclient

@author: scanlom
'''

from os import path
from ofxclient.config import OfxConfig
from ofxparse import OfxParser
from psycopg2 import connect
from psycopg2.extras import DictCursor       
from api_config import config_database_connect
from api_log import log

def main():
    log.info("Started...")
        
    conn = connect( config_database_connect )
    cur = conn.cursor(cursor_factory=DictCursor)
    sql = "select * from accounts_types where download=true";
    cur.execute(sql)
    banks = cur.fetchall()   
    for bank in banks:
        try:
            log.info("Downloading: " + " " + bank['description'])
            GlobalConfig = OfxConfig()
            a = GlobalConfig.account(bank['id'])
            ofxdata = a.download(days=0)
            f = open(path.expanduser('~/tmp/ofxdata.tmp'), 'w')
            f.write(ofxdata.read())
            f.close()
            f = open(path.expanduser('~/tmp/ofxdata.tmp'), 'r')
            parsed = OfxParser.parse(f)
            f.close()
            log.info("OfxParser complete")
            positions = {}
            for pos in parsed.account.statement.positions:
                positions[pos.security] = round(pos.units * pos.unit_price, 2)
                log.info("Downloaded: " + str(bank['description']) + " " + str(pos.security))
            
            sql = "select * from accounts where type=" + str(bank['type']);
            cur.execute(sql)
            accounts = cur.fetchall()
            for account in accounts:
                if account['name'] not in positions:
                    raise Exception('account ' + account['name'] + ' not present in download')
                log.info( bank['description'] + '\t' + account['name_local'] + '\t' + str(positions[account['name']]) ) 
                sql = "update constituents set value=" + str(positions[account['name']]) + "where symbol='" + account['name_local'] + "'"
                cur.execute(sql)
                conn.commit()
                log.info("Set: " + str(account['name_local']))
                
        except Exception as err:
            log.exception(err)
            log.error("Failed loading for bank: " + bank['description'])
    
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