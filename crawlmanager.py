#!/usr/bin/python
# -*- coding: utf-8 -*-

import log
import globalconfig as GC
import time
import threading
import signal

from database import createProdDataBase
import database

from resourcepool import createProdRenrenAccountPool
from proxypool import createProdProxyPool
from resourcepool import RenrenAccountPool

from crawler import Crawler
from crawler import CrawlerException
from crawler import CrawlerErrorCode
from proxy import Proxy

import threading

currentCrawler = None
stopSignal = False

def detectSignal(a, b):
    print "INT Signal detect"
    Crawler.setStopSignal()


class CrawlThread(threading.Thread):
    """A single crawling thread."""
    threadId = 0
    accountLimit = 10
    dataBase = None
    renrenAccountPool = None
    proxy = None

    def __init__(self, tid, dataBase, pool, accountLimit, proxy=None):
        threading.Thread.__init__(self)
        log.info("Create thread " + str(tid))
        self.threadId = tid
        self.dataBase = dataBase
        self.renrenAccountPool = pool
        self.accountLimit = accountLimit
        self.proxy = proxy

    def run(self):
        log.info("Thread " + str(self.threadId) + ": run......")
        for i in range(0, self.accountLimit):
            account = self.renrenAccountPool.getAccount()
            try:
                id, tableId = self.dataBase.getStartNode()
                if not account or not id:
                    log.warning('Thread ' + str(self.threadId) +\
                        ': No account or start node!')
                    break
                time.sleep(0.8)
                self.singleCrawl(account, id)
            except CrawlerException, e:
                break
            finally:
                # These dispose may also be done in crawler.dispose()
                if account: account.dispose()
                if tableId: self.dataBase.releaseStartNode(tableId)

    def singleCrawl(self, account, startId):
        crawler = Crawler()
        try:
            crawler.init(account, self.dataBase, self.proxy)
            crawler.crawl(startId, 100)
        except CrawlerException, e:
            log.info("Thread " + str(self.threadId) +\
                " Crawler end with exception, reason: " + str(e))
            if e.errorCode == CrawlerErrorCode.DETECT_STOP_SIGNAL:
                raise e
            elif e.errorCode == CrawlerErrorCode.GET_EXPANDING_NODE_FAILED or\
                e.errorCode == CrawlerErrorCode.EXPAND_EXPANDED_NODE:
                self.dataBase.deleteFromStartList(startId)
        finally:
            crawler.dispose()


class CrawlManager:

    accountLimit = 40
    dataBase = None
    renrenAccountPool = None

    def startMultiThreadCrawling(self, threadNumber):
        self.dataBase = createProdDataBase()
        self.dataBase.releaseAllStartNode()
        self.renrenAccountPool = createProdRenrenAccountPool()

        threads = []
        for i in range(0, threadNumber):
            thread = CrawlThread(
                i, self.dataBase, self.renrenAccountPool, self.accountLimit)
            threads.append(thread)
            thread.start()
            time.sleep(1.5)

        # Wait for a signal
        signal.pause()

        for thread in threads:
            thread.join()
        log.info("Main thread end....")

    def startSignleThreadCrawling(self):
        self.dataBase = createProdDataBase()
        self.dataBase.releaseAllStartNode()
        self.renrenAccountPool = createProdRenrenAccountPool()
        thread = CrawlThread(
            0, self.dataBase, self.renrenAccountPool, self.accountLimit)
        thread.run()
    
    def startMultiThreadCrawlingWithProxy(self, threadNumber):
        self.dataBase = createProdDataBase()
        self.dataBase.releaseAllStartNode()
        self.renrenAccountPool = createProdRenrenAccountPool()
        pool = createProdProxyPool()
        proxies = pool.getProxies(threadNumber)

        threads = []
        for i in range(0, threadNumber):
            thread = CrawlThread(
                i, self.dataBase, self.renrenAccountPool, self.accountLimit,
                proxies[i])
            threads.append(thread)
            thread.start()
            time.sleep(1.5)

        # Wait for a signal
        signal.pause()

        for thread in threads:
            thread.join()
        log.info("Main thread end....")

        
def main():
    log.config(GC.LOG_FILE_DIR + 'CrawlManager', 'info', 'info')
    signal.signal(signal.SIGINT, detectSignal)
    manager = CrawlManager()
    manager.startMultiThreadCrawling(5)
    #manager.startMultiThreadCrawlingWithProxy(3)
    #manager.startSignleThreadCrawling()

if __name__ == "__main__":
    main()
