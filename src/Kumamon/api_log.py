'''
Created on Dec 25, 2013

@author: scanlom
'''

from logging import getLogger
from logging import Formatter
from logging import INFO 
from logging import handlers
from logging import StreamHandler
from os import path

log = getLogger()
log.setLevel(INFO)

formatter = Formatter(
    "%(asctime)s %(module)-11s %(levelname)-10s %(message)s")

# Log to file - 50k max, 5 files
filehandler = handlers.RotatingFileHandler(path.expanduser('~/logs/Kumamon.log'), 50*1024, 5)
filehandler.setLevel(INFO)
filehandler.setFormatter(formatter)
log.addHandler(filehandler)

# Log to stdout also
streamhandler = StreamHandler()
streamhandler.setLevel(INFO)
streamhandler.setFormatter(formatter)
log.addHandler(streamhandler)