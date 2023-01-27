'''
Created on Feb 6, 2022

@author: scanlom
'''

import json as _json
import re as _re
import requests as _requests
from api_log import log

# New code after Yahoo started encrypting things (Post 2022/12/31)
# https://github.com/ranaroussi/yfinance/commit/8e5f0984af347afda6be74b27a989422e49a975b
import hashlib
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

CONST_URL_QUOTE = 'https://finance.yahoo.com/quote'
CONST_FORMAT_URL_HISTORICALS = 'https://finance.yahoo.com/quote/{}/history?period1=0&period2=9999999999&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true'
CONST_HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
CONST_TIMEOUT = 10

def get_json( url ):
    html = _requests.get(url=url, headers=CONST_HEADERS, timeout=CONST_TIMEOUT).text
    json_str = html.split('root.App.main =')[1].split(
        '(this)')[0].split(';\n}')[0].strip()
    
    # Old code before Yahoo started encrypting things (Pre 2022/12/31)
    """data = _json.loads(json_str)[
        'context']['dispatcher']['stores']
    # return data
    data = _json.dumps(data).replace('{}', 'null')
    data = _re.sub(
        r'\{[\'|\"]raw[\'|\"]:(.*?),(.*?)\}', r'\1', data)

    return _json.loads(data)"""

    # New code after Yahoo started encrypting things (Post 2022/12/31)
    data = _json.loads(json_str)
    encrypted_stores = data['context']['dispatcher']['stores']
    if "_cs" in data and "_cr" in data:
        _cs = data["_cs"]
        _cr = data["_cr"]
        _cr = b"".join(int.to_bytes(i, length=4, byteorder="big", signed=True) for i in json.loads(_cr)["words"])
        password = hashlib.pbkdf2_hmac("sha1", _cs.encode("utf8"), _cr, 1, dklen=32).hex()
    else:
        # Currently assume one extra key in dict, which is password. Print error if 
        # more extra keys detected.
        new_keys = [k for k in data.keys() if k not in ["context", "plugins"]]
        l = len(new_keys)
        if l == 0:
            return None
        elif l == 1 and isinstance(data[new_keys[0]], str):
            password_key = new_keys[0]
        else:
            msg = "Yahoo has again changed data format, yfinance now unsure which key(s) is for decryption:"
            k = new_keys[0]
            k_str = k if len(k) < 32 else k[:32-3]+"..."
            msg += f" '{k_str}'->{type(data[k])}"
            for i in range(1, len(new_keys)):
                msg += f" , '{k_str}'->{type(data[k])}"
            raise Exception(msg)
        password_key = new_keys[0]
        password = data[password_key]

    encrypted_stores = b64decode(encrypted_stores)
    assert encrypted_stores[0:8] == b"Salted__"
    salt = encrypted_stores[8:16]
    encrypted_stores = encrypted_stores[16:]

    def EVPKDF(
        password,
        salt,
        keySize=32,
        ivSize=16,
        iterations=1,
        hashAlgorithm="md5",
    ) -> tuple:
        """OpenSSL EVP Key Derivation Function
        Args:
            password (Union[str, bytes, bytearray]): Password to generate key from.
            salt (Union[bytes, bytearray]): Salt to use.
            keySize (int, optional): Output key length in bytes. Defaults to 32.
            ivSize (int, optional): Output Initialization Vector (IV) length in bytes. Defaults to 16.
            iterations (int, optional): Number of iterations to perform. Defaults to 1.
            hashAlgorithm (str, optional): Hash algorithm to use for the KDF. Defaults to 'md5'.
        Returns:
            key, iv: Derived key and Initialization Vector (IV) bytes.
        Taken from: https://gist.github.com/rafiibrahim8/0cd0f8c46896cafef6486cb1a50a16d3
        OpenSSL original code: https://github.com/openssl/openssl/blob/master/crypto/evp/evp_key.c#L78
        """

        assert iterations > 0, "Iterations can not be less than 1."

        if isinstance(password, str):
            password = password.encode("utf-8")

        final_length = keySize + ivSize
        key_iv = b""
        block = None

        while len(key_iv) < final_length:
            hasher = hashlib.new(hashAlgorithm)
            if block:
                hasher.update(block)
            hasher.update(password)
            hasher.update(salt)
            block = hasher.digest()
            for _ in range(1, iterations):
                block = hashlib.new(hashAlgorithm, block).digest()
            key_iv += block

        key, iv = key_iv[:keySize], key_iv[keySize:final_length]
        return key, iv

    key, iv = EVPKDF(password, salt, keySize=32, ivSize=16, iterations=1, hashAlgorithm="md5")

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    plaintext = cipher.decrypt(encrypted_stores)
    plaintext = unpad(plaintext, 16, style="pkcs7")
    decoded_stores = _json.loads(plaintext)

    return decoded_stores

def get_quote( ticker ):
    return get_json( "{}/{}".format(CONST_URL_QUOTE, ticker ) )

def get_financials( ticker ):
    return get_json( "{}/{}/financials".format(CONST_URL_QUOTE, ticker ) )

def get_historicals( ticker ):
    return get_json( CONST_FORMAT_URL_HISTORICALS.format( ticker ) )

def main():
    log.info("Started...")
    
    ticker = "MSFT"
    historicals = get_historicals( ticker )
    print( historicals['HistoricalPriceStore']['prices'][0] )

    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)