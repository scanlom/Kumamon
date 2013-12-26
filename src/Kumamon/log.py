'''
Created on Dec 25, 2013

@author: scanlom
'''

import logging, os
import logging.handlers

log = logging.getLogger()
log.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

# Log to file - 50k max, 5 files
filehandler = logging.handlers.RotatingFileHandler(os.path.expanduser('~/logs/Kumamon.log'), 50*1024, 5)
filehandler.setLevel(logging.INFO)
filehandler.setFormatter(formatter)
log.addHandler(filehandler)

# Log to stdout also
streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.INFO)
streamhandler.setFormatter(formatter)
log.addHandler(streamhandler)