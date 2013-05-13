#!/usr/bin/python
#-*-coding:utf-8 -*-

import sys
sys.path.append('..')

import log
import globalconfig as GC
import confidential as CFD
import time
import threading
import urllib2

from bs4 import BeautifulSoup
from proxypool import ProxyPool
from proxypool import createProdProxyPool
from proxy import Proxy
from proxy import ProxyTester

from threadpool import ThreadPool


class PageParser:
    """A class that can parse page to proxies."""
    
    def parse(self, html, source):
        """Parse a html page, and return all contained proxy."""
        document = BeautifulSoup(html)
        content = document.find('p')
        proxies = []
        if content:
            for string in content.stripped_strings:
                proxy = Proxy.parse(string, source)
                if proxy:
                    proxies.append(proxy)
        else:
            log.warning('Can not find content element.')
        return proxies
        


class CrawlingThread(threading.Thread):
    """A thread making HTTP request to proxy source page."""
    url = 'http://www.renren.com'
    parser = None
    importer = None

    def __init__(self, url, parser, importer):
        threading.Thread.__init__(self)
        self.url = url
        self.parser = parser
        self.importer = importer

    def run(self):
        try:
            opener = urllib2.build_opener()
            html = opener.open(self.url, timeout=10)
            proxies = self.parser.parse(html, self.url)
            for proxy in proxies:
                self.importer.addProxy(proxy)
            log.debug('Crawl proxies from ' + str(self.url) + ':')
            for proxy in proxies:
                log.debug('>>>>>' + proxy.getAllString())
        except Exception, e:
            log.warning('Crawling thread exception: ' + str(e))



class ProxyImporter:
    
    allProxies = [] # All the proxies crawled.
    LOCK = threading.RLock() # Lock of allProxies

    def addProxy(self, proxy):
        self.LOCK.acquire()
        self.allProxies.append(proxy)
        self.LOCK.release()

    def getProxyCount(self):
        self.LOCK.acquire()
        count = len(self.allProxies)
        self.LOCK.release()
        return count


    def crawlFromItmop(self):
        prefix = 'http://www.itmop.com/proxy/post/'
        parser = PageParser()
        threads = []
        for i in range(1330, 1331 + 1):
            url = prefix + str(i) + '.html'
            thread = CrawlingThread(url, parser, self)
            threads.append(thread)

        pool = ThreadPool(40)
        pool.start(threads)


    def crawlAll(self):
        self.crawlFromItmop()
        log.info('Crawling stage finish.  Total proxy number: ' +\
            str(self.getProxyCount()))

    def removeDuplicate(self):
        proxyMap = {}
        for proxy in self.allProxies:
            key = proxy.addr[0 : proxy.addr.rfind('.')]
            if not proxyMap.get(key):
                proxyMap[key] = proxy

        self.proxiesToTest = [item[1] for item in proxyMap.items()]
        log.info( 'After remove duplicate, proxy number: ' +\
            str(len(self.proxiesToTest)))

    def investigate(self):
        self.allProxies.sort(key=lambda x: x.addr)
        for proxy in self.allProxies:
            log.info(str(proxy.averageTime) + '    ' +\
                str(proxy.successCount) + '/' +\
                str(proxy.testCount) + '    ' +\
                proxy.getAllString())

    def testAll(self):
        startTime = time.time()
        threads = []
        proxies = self.proxiesToTest
        for proxy in proxies:
            tester = ProxyTester(proxy)
            threads.append(tester)

        pool = ThreadPool(40)
        pool.start(threads)
        
        log.info( 'Test finish.  Total test time:  ' +\
            str(time.time() - startTime) + 's')
        #allProxies.sort(key=lambda x: x.averageTime)
        #for i in range(0, 200):
        #    if i >= len(allProxies):
        #        return
        #    proxy = allProxies[i]

    def importAll(self):
        pool = createProdProxyPool()
        pool.deleteAllProxies()
        proxies = self.proxiesToTest
        proxies.sort(key=lambda x: x.averageTime)
        for i in range(0, 200):
            if i >= len(proxies):
                break
            proxy = proxies[i]
            pool.insertProxy(proxy)

    
    def start(self):
        self.crawlAll()
        self.removeDuplicate()
        self.testAll()
        #self.investigate()
        self.importAll()

def main():
    reload(sys)
    sys.setdefaultencoding("utf-8")
    log.config(GC.LOG_FILE_DIR + 'import_proxies', 'info', 'info')
    #log.config(GC.LOG_FILE_DIR + 'import_proxies', 'debug', 'debug')
    importer = ProxyImporter()
    importer.start()

if __name__ == "__main__":
  main();
