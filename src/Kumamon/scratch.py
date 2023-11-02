'''
Created on February 2, 2023
@author: scanlom
'''

import requests
from json import loads
from lib_log import log

def main():
    log.info("Started...")
    
    url_format = "https://uatapi.sixbulkapi.com/COMPLY/apps/v1/z/six-reference/listing/%s?api-key=04d4C75igC8eDqldCOloXWfnTIdLOk08lOlRpEt3"
    url_base_token = "latest"
    num_products = 0
    map_cols = {}
    map_num_products = {}
    map_swiss = {}
    swiss_unique = True
    MAX_LOAD = 20000
    response = requests.get(url_format % (url_base_token))
    json = loads(response.text)
    for node in json['data']:
        response_mic = requests.get(url_format % (node['href']))
        json_mic = loads(response_mic.text)
        for node_product in json_mic['data']:
            response_product = requests.get(url_format % (node_product['href']))
            json_product = loads(response_product.text)
            if num_products >= MAX_LOAD:
                break
            num_products += 1
            instrumentClassificationBySIX = "NONE"
            if 'instrumentClassificationBySIX' in json_product['data']['instrument']:
                instrumentClassificationBySIX = json_product['data']['instrument']['instrumentClassificationBySIX']
            isin = "NONE"
            if 'ISIN' in json_product['data']['instrument']:
                isin = json_product['data']['instrument']['ISIN']
            swiss = json_product['data']['instrument']['swissValorNumber']
            if swiss in map_swiss:
                swiss_unique = False
            else:
                map_swiss[swiss] = True
            print("%d, %s, %s, %s" % (num_products, isin, json_product['data']['instrument']['FISN'], instrumentClassificationBySIX))
            map_inner = {}
            if instrumentClassificationBySIX in map_cols:
                map_inner = map_cols[instrumentClassificationBySIX]
            if instrumentClassificationBySIX in map_num_products:
                map_num_products[instrumentClassificationBySIX] = map_num_products[instrumentClassificationBySIX] + 1
            else:
                 map_num_products[instrumentClassificationBySIX] = 1
            for key in json_product['data']:
                if key not in ['issuer', 'instrument', 'listing', 'lastUpdated']:
                    print("unkown product data key " + key)
                if key == 'lastUpdated':
                    continue
                for col in json_product['data'][key]:
                    # Hash all the keys by instrument.instrumentClassificationBySIX
                    map_inner[key + "." + col] = True
            map_cols[instrumentClassificationBySIX] = map_inner
        if num_products >= MAX_LOAD:
            break
    for instrumentClassificationBySIX in map_cols:
        print("instrumentClassificationBySIX is " + instrumentClassificationBySIX)
        print("num products: " + str(map_num_products[instrumentClassificationBySIX]))
        cols = map_cols[instrumentClassificationBySIX]
        for col in cols:
            print(col)
    print("num products total: %d" % (num_products) )
    if swiss_unique:
        print("Swiss unique")
    else:
        print("Swiss not unique")
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 