# The simple logger
# This logger base on logging module
import logging
from time import localtime
from time import strftime

"""
There are two log target: standard print and file system.
Standard print means logging will print message at the console.
File system means logging will save as a log file in the disk.
The two target have two seperated message level:(printLevel, fileLevel)
The level can be one of 5 different state (same as logging module):
  DEBUG, INFO, WARNING, ERROR, CRITICAL
"""
__DEBUG__ = 0
__INFO__ = 1
__WARNING__ = 2
__ERROR__ = 3
__CRITICAL__ = 4

__LEVEL_MAP__ = {'DEBUG':0, 'debug':0,
                 'INFO':1, 'info':1,
                 'WARNING':2, 'warning':2,
                 'ERROR':3, 'error':3,
                 'CRITICAL':4, 'critical':4}
                 
__LEVEL_REV_MAP__ = {0:'DEBUG',
                 1:'INFO',
                 2:'WARNING',
                 3:'ERROR',
                 4:'CRITICAL'}

__PRINT_LEVEL__ = __WARNING__
__FILE_LEVEL__ = __WARNING__
  
__LOG_TO_FILE__ = False
  
# Config the log file, log level, print file
# It should be called only once
def config(logFileName, fileLevel=None, printLevel=None):
  #print logFileName, fileLevel, printLevel
  global __LOG_TO_FILE__
  global __PRINT_LEVEL__
  global __FILE_LEVEL__
  
  if logFileName:
    __LOG_TO_FILE__ = True
    logFileName += '-' + strftime('%y-%m-%d-%H:%M:%S', localtime())
  
  if fileLevel and fileLevel in __LEVEL_MAP__:
    __FILE_LEVEL__ = __LEVEL_MAP__[fileLevel]
    
  if printLevel and printLevel in __LEVEL_MAP__:
    __PRINT_LEVEL__ = __LEVEL_MAP__[printLevel]
    
  loggingLevelCode = getattr(logging, __LEVEL_REV_MAP__[__FILE_LEVEL__], None)

  if __LOG_TO_FILE__: 
    logging.basicConfig(format='%(levelname)s--%(asctime)s:  %(message)s', 
                        datefmt='%m/%d/%Y %I:%M:%S %p', 
                        filename = logFileName, 
                        level = loggingLevelCode)
  else:
    logging.basicConfig(format='%(levelname)s--%(asctime)s:  %(message)s', 
                        datefmt='%m/%d/%Y %I:%M:%S %p', 
                        level = loggingLevelCode)  

def debug(message):
  logging.debug(message)
  if __PRINT_LEVEL__ <= __DEBUG__:
    print 'DEBUG:  ' + message

def info(message):
  logging.info(message)
  if __PRINT_LEVEL__ <= __INFO__:
    print 'INFO:  ' + message
  
def warning(message):
  logging.warning(message)
  if __PRINT_LEVEL__ <= __WARNING__:
    print 'WARNING:  ' + message
  
def error(message):
  logging.error(message)
  if __PRINT_LEVEL__ <= __ERROR__:
    print 'ERROR:  ' + message
  
def critical(message):
  logging.critical(message)
  if __PRINT_LEVEL__ <= __CRITICAL__:
    print 'CRITICAL:  ' + message

# This means this message is a warning but there are too many
# possible warning, treat it as a warning in file log target, 
#but as a debug in print log target
def noisyWarning(message):
  logging.warning(message)
  if __PRINT_LEVEL__ <= __DEBUG__:
    print 'DEBUG:  ' + message


def __LOG__(message):
  debug('debug-' + message)
  info('info-' + message)
  warning('warning-' + message)
  error('error-' + message)
  critical('critical-' + message)
  noisyWarning('noisyWarning-' + message)

def test():
  config('tmp.log', 'error', 'info')
  critical('==============start log test===============')
  __LOG__('message')  

if __name__ == '__main__': test()
  
  
