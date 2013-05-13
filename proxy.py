#!/usr/bin/python
#-*-coding:utf-8 -*-

import bs4
import re
import threading
import urllib2
import time
import log

from bs4 import BeautifulSoup
from threadpool import ThreadPool


class ProxyTester(threading.Thread):
    """A thread making HTTP request to test the proxy."""
    proxy = None
    url = 'http://www.baidu.com'
    totalTestNumber = 5
    acceptableFailTestNumber = 1

    def __init__(self, proxy, url=None, total=5, fail=2):
        threading.Thread.__init__(self)
        self.proxy = proxy
        if url:
            self.url = url
        self.totalTestNumber = total
        self.acceptableFailTestNumber = fail

    def run(self):
        totalTestCount = 0
        totalWaitingTime = 0
        successCount = 0
        failCount = 0

        for i in range(0, self.totalTestNumber):
            success, waitingTime = self.makeRequest()
            if success:
                successCount += 1
                totalWaitingTime += waitingTime
            else:
                failCount += 1
                totalWaitingTime += 10000
            totalTestCount += 1
            if failCount >= self.acceptableFailTestNumber:
                break
            time.sleep(1)

        if successCount >= 1:
            averageTime = float(totalWaitingTime) / successCount
        else:
            averageTime = 9999999
        self.proxy.averageTime = averageTime
        self.proxy.testCount = totalTestCount
        self.proxy.successCount = successCount

        log.debug('Finish single proxy test:  ' +\
            str(self.proxy.averageTime) + '    ' +\
            str(self.proxy.successCount) + '/' + str(self.proxy.testCount) +\
            '    ' + self.proxy.getAllString())
        

    def makeRequest(self):
        success = False
        startTime = time.time()
        try:
            protocol = self.proxy.protocol
            if not protocol:
                # Default to HTTP protocol
                protocol = 'HTTP'
            proxy_handler = urllib2.ProxyHandler({
                protocol: self.proxy.getProxyString()
            })
            opener = urllib2.build_opener(proxy_handler)
            response = opener.open(self.url, timeout=3)
            response.read()
            success = True
        except Exception, e:
            log.info('Fail on proxy test:  ' + str(e) + ' ' +\
                self.proxy.getAllString())

        return (success, (time.time() - startTime)*1000)


class Proxy:
    """ The class represents a proxy."""
    addr = None # The address of the proxy.
    port = None # The port.
    protocol = None # Supported protocol.
    info = None # Releated info, if given any.
    source = None # Where this proxy come from.

    testCount = 0 # Total test times count.
    successCount = 0 # Count of success test.
    averageTime = 999999 # Average waiting time, in ms.


    # Parse something like:
    #   221.181.192.91:80@HTTP;江苏省无锡市 移动
    #   68 187.86.0.183 3129 HTTP 巴西 itmop.com 10-22 14:04 11.012 whois
    pat1 = re.compile(
        '.*[\s]?' +\
        '(\d+\.\d+\.\d+\.\d+)' +\
        '[:\s]' +\
        '(\d+)' +\
        '[@\s]' +\
        '(\w*)' +\
        '(.*)')

    def __init__(self, source=None):
        self.source = source
    
    def parse_(self, string):
        """Parse the string to get a proxy."""
        mat = self.pat1.match(string)
        if mat:
            self.addr = mat.group(1)
            self.port = mat.group(2)
            self.protocol = mat.group(3)
            self.info = mat.group(4)
            
    def getAllString(self):
        return self.addr+ ':' + self.port + '@' +\
            str(self.protocol) + ' >>> ' + str(self.info)  + '  >>>  ' +\
            str(self.source)

    def getProxyString(self):
        return self.addr + ':' + self.port

    @staticmethod
    def parse(string, source=None):
        """Parses a string and return a proxy object."""
        proxy = Proxy(source)
        proxy.parse_(string)
        if not proxy.addr or not proxy.port:
            # Not a valid proxy.
            return None
        return proxy
