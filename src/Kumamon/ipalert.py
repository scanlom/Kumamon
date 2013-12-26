'''
Created on Oct 14, 2013

@author: scanlom
'''

import os.path, mail
from urllib.request import urlopen
from log import log

def main():
    log.info("Started...")
    
    # Get my ip
    url = 'http://curlmyip.com'
    str = urlopen(url).read()
    my_ip = str.decode().strip()
    
    filename = os.path.expanduser('~/.Myip')
    saved_ip = ""
    
    if os.path.isfile(filename):
        f = open(filename, 'r')
        saved_ip = f.read()
        f.close()
        
    if my_ip != saved_ip:
        mail.send_mail_html_self('New IP!','http://' + my_ip + ':3000')
        log.info("IP modified from " + saved_ip + " to " + my_ip)
        f = open(filename, 'w')
        f.write(my_ip)
        f.close()
    else:
        log.info("IP remains " + saved_ip)
        
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted")
        mail.send_mail_html_self("FAILURE:  ipalert.py", str( err ) ) 