'''
Created on Dec 25, 2013

@author: scanlom
'''

from logging import getLogger
from logging import Formatter
from logging import INFO
from logging import ERROR
from logging import handlers
from logging import StreamHandler
from os import path
from sys import argv
from api_mail import send_mail_html_self

CONST_NUM_FILES     = 5
CONST_SIZE_FILE     = 50*1024
CONST_SIZE_EMAIL    = 100

log = getLogger()
log.setLevel(INFO)

formatter = Formatter(
    "%(asctime)s %(module)-11s %(levelname)-10s %(message)s")

# Log to file - 50k max, 5 files
filehandler = handlers.RotatingFileHandler(path.expanduser('~/logs/Kumamon.log'), maxBytes=CONST_SIZE_FILE, backupCount=CONST_NUM_FILES)
filehandler.setLevel(INFO)
filehandler.setFormatter(formatter)
log.addHandler(filehandler)

# Log to stdout also
streamhandler = StreamHandler()
streamhandler.setLevel(INFO)
streamhandler.setFormatter(formatter)
log.addHandler(streamhandler)

class BufferingSMTPHandler(handlers.BufferingHandler):
    def __init__(self):
        handlers.BufferingHandler.__init__(self, CONST_SIZE_EMAIL)
        self.subject = argv[0] + " errors"

    def flush(self):
        if len(self.buffer) > 0:
            try:
                msg = ""
                for record in self.buffer:
                    s = self.format(record)
                    msg = msg + s + "\r\n"
                send_mail_html_self(self.subject, msg)
            except:
                self.handleError(None)  # no particular record
            self.buffer = []
            
# Log to email also
emailHandler = BufferingSMTPHandler()
emailHandler.setLevel(ERROR)
emailHandler.setFormatter(formatter)
log.addHandler(emailHandler)

def main():
    log.info("Started...")
    
    # Test
    for i in range(101):
        log.error("Mikey")
    
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 
            