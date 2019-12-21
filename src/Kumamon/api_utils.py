'''
Created on Dec 8, 2019

@author: scanlom
'''

from requests import get
from api_log import log

def confidence( research ):
    # MSTODO - Desperately need to move this to post
    url = 'http://localhost:8080/blue-lion/utils/confidence?research=%s' % ("".join(research.split()).replace('%',''))
    response = get(url)
    return response.json()['confidence']

def cagr( years, eps, payout, growth, pe_terminal, price ):
    url = 'http://localhost:8080/blue-lion/utils/cagr?years=%f&eps=%f&payout=%f&growth=%f&peterminal=%f&price=%f' % (years, eps, payout, growth, pe_terminal, price)
    response = get(url)
    return response.json()['cagr']

def main():
    log.info("Started...")
    
    # Test
    print(cagr(5, 2.16, 0, 0.15, 15, 41.61))
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)