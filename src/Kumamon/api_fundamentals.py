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
import time
import random
from base64 import b64decode
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

CONST_URL_QUOTE = 'https://finance.yahoo.com/quote'
CONST_FORMAT_URL_HISTORICALS = 'https://finance.yahoo.com/quote/{}/history?period1=0&period2=9999999999&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true'
CONST_HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
CONST_TIMEOUT = 10

def extract_extra_keys_from_stores(data):
    new_keys = [k for k in data.keys() if k not in ["context", "plugins"]]
    new_keys_values = set([data[k] for k in new_keys])

    # Maybe multiple keys have same value - keep one of each
    new_keys_uniq = []
    new_keys_uniq_values = set()
    for k in new_keys:
        v = data[k]
        if not v in new_keys_uniq_values:
            new_keys_uniq.append(k)
            new_keys_uniq_values.add(v)

    return new_keys_uniq

def get_decryption_keys_from_yahoo_js(soup):
    result = None

    key_count = 4
    re_script = soup.find("script", string=_re.compile("root.App.main")).text
    re_data = _json.loads(_re.search("root.App.main\s+=\s+(\{.*\})", re_script).group(1))
    re_data.pop("context", None)
    key_list = list(re_data.keys())
    if re_data.get("plugins"):  # 1) attempt to get last 4 keys after plugins
        ind = key_list.index("plugins")
        if len(key_list) > ind+1:
            sub_keys = key_list[ind+1:]
            if len(sub_keys) == key_count:
                re_obj = {}
                missing_val = False
                for k in sub_keys:
                    if not re_data.get(k):
                        missing_val = True
                        break
                    re_obj.update({k: re_data.get(k)})
                if not missing_val:
                    result = re_obj

    if not result is None:
        return [''.join(result.values())]

    re_keys = []    # 2) attempt scan main.js file approach to get keys
    prefix = "https://s.yimg.com/uc/finance/dd-site/js/main."
    tags = [tag['src'] for tag in soup.find_all('script') if prefix in tag.get('src', '')]
    for t in tags:
        response_js = _requests.get(url=t, headers=CONST_HEADERS, timeout=CONST_TIMEOUT)
        #
        if response_js.status_code != 200:
            time.sleep(random.randrange(10, 20))
            response_js.close()
        else:
            r_data = response_js.content.decode("utf8")
            re_list = [
                x.group() for x in _re.finditer(r"context.dispatcher.stores=JSON.parse((?:.*?\r?\n?)*)toString", r_data)
            ]
            for rl in re_list:
                re_sublist = [x.group() for x in _re.finditer(r"t\[\"((?:.*?\r?\n?)*)\"\]", rl)]
                if len(re_sublist) == key_count:
                    re_keys = [sl.replace('t["', '').replace('"]', '') for sl in re_sublist]
                    break
            response_js.close()
        if len(re_keys) == key_count:
            break
    re_obj = {}
    missing_val = False
    for k in re_keys:
        if not re_data.get(k):
            missing_val = True
            break
        re_obj.update({k: re_data.get(k)})
    if not missing_val:
        return [''.join(re_obj.values())]

    return []

def get_json( url ):
    response = _requests.get(url=url, headers=CONST_HEADERS, timeout=CONST_TIMEOUT)
    json_str = response.text.split('root.App.main =')[1].split(
        '(this)')[0].split(';\n}')[0].strip()

    data = _json.loads(json_str)

    # Gather decryption keys:
    soup = BeautifulSoup(response.content, "html.parser")
    keys = get_decryption_keys_from_yahoo_js(soup)
    if len(keys) == 0:
        msg = "No decryption keys could be extracted from JS file."
        if "requests_cache" in str(type(response)):
            msg += " Try flushing your 'requests_cache', probably parsing old JS."
        print("WARNING: " + msg + " Falling back to backup decrypt methods.")
    if len(keys) == 0:
        keys_url = "https://github.com/ranaroussi/yfinance/raw/main/yfinance/scrapers/yahoo-keys.txt"
        response_gh = _requests.get(url=keys_url, headers=CONST_HEADERS, timeout=CONST_TIMEOUT)
        keys = response_gh.text.splitlines()
        extra_keys = extract_extra_keys_from_stores(data)
        if len(extra_keys) < 10:
            # Only brute-force with these extra keys if few
            keys += extra_keys

    encrypted_stores = data['context']['dispatcher']['stores']
    password = None
    if keys is not None:
        if not isinstance(keys, list):
            raise TypeError("'keys' must be list")
        candidate_passwords = keys
    else:
        candidate_passwords = []

    if "_cs" in data and "_cr" in data:
        _cs = data["_cs"]
        _cr = data["_cr"]
        _cr = b"".join(int.to_bytes(i, length=4, byteorder="big", signed=True) for i in json.loads(_cr)["words"])
        password = hashlib.pbkdf2_hmac("sha1", _cs.encode("utf8"), _cr, 1, dklen=32).hex()

    encrypted_stores = b64decode(encrypted_stores)
    assert encrypted_stores[0:8] == b"Salted__"
    salt = encrypted_stores[8:16]
    encrypted_stores = encrypted_stores[16:]

    def _EVPKDF(
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

    def _decrypt(encrypted_stores, password, key, iv):
        #if usePycryptodome:
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        plaintext = cipher.decrypt(encrypted_stores)
        plaintext = unpad(plaintext, 16, style="pkcs7")
        """else:
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(encrypted_stores) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(plaintext) + unpadder.finalize()
            plaintext = plaintext.decode("utf-8")"""
        return plaintext

    if not password is None:
        try:
            key, iv = _EVPKDF(password, salt, keySize=32, ivSize=16, iterations=1, hashAlgorithm="md5")
        except:
            raise Exception("yfinance failed to decrypt Yahoo data response")
        plaintext = _decrypt(encrypted_stores, password, key, iv)
    else:
        success = False
        for i in range(len(candidate_passwords)):
            # print(f"Trying candiate pw {i+1}/{len(candidate_passwords)}")
            password = candidate_passwords[i]
            try:
                key, iv = _EVPKDF(password, salt, keySize=32, ivSize=16, iterations=1, hashAlgorithm="md5")

                plaintext = _decrypt(encrypted_stores, password, key, iv)

                success = True
                break
            except:
                pass
        if not success:
            raise Exception("yfinance failed to decrypt Yahoo data response")

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