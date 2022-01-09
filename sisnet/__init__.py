"""
Module initializations. We just configure here the logger.
"""
__author__ = "Jonatan Morales"
__version__ = "beta.20211127"

import logging
import logging.handlers
from logging.config import fileConfig

# Logging basic config to console
logging.basicConfig(
	format='%(asctime)s [%(levelname)-5s] [%(filename)s:%(lineno)d] %(message)s',
	datefmt='%Y-%m-%d %H:%m',
	level=logging.DEBUG
)

# Log
log = logging.getLogger('sisnet')

# Logging to file
# LOGFILE = 'sisnet.log'
# fileHandler = logging.handlers.RotatingFileHandler(LOGFILE, maxBytes=(1048576*5), backupCount=5)
# logFormat = logging.Formatter(
# 	'%(asctime)s [%(levelname)-5s] [%(filename)s:%(lineno)d] %(message)s',
# 	datefmt='%Y-%m-%d %H:%M'
# )
# fileHandler.setFormatter(logFormat)
# fileHandler.setLevel(logging.DEBUG)
# log.addHandler(fileHandler)
