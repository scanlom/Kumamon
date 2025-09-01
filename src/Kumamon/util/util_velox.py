'''
Created on July 7, 2025
@author: scanlom
'''

import requests
from json import loads
from lib_log import log

def main():
    log.info("Started...")
    
    token = 'ultumus-login'
    url = 'https://ironhide.ultumus.com/'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url=url, headers=headers)
    if token not in response.text:
        raise Exception("Ironhide login screen not found!")

    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 