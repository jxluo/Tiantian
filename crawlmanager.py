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
from resourcepool import RenrenAccountPool

from crawler import Crawler
from crawler import CrawlerException
from crawler import CrawlerErrorCode

currentCrawler = None
stopSignal = False

def detectSignal(a, b):
    print "Signal detect"
    global currentCrawler
    global stopSignal
    stopSignal = True
    if currentCrawler:
        currentCrawler.setStopSignal()

class CrawlManager:

    accountLimit = 100

    dataBase = None
    renrenAccountPool = None

    def __init__(self):
        pass

    def startCrawling(self):
        self.dataBase = createProdDataBase()
        self.renrenAccountPool = createProdRenrenAccountPool()
        accounts = self.renrenAccountPool.getAccounts(self.accountLimit) 
        for account in accounts:
            ids = self.dataBase.getStartNodes(1)
            if len(ids) == 0:
                log.error('No node in start list, end process.')
                return
            if stopSignal:
                return
            self.singleCrawl(account, ids[0])

    def singleCrawl(self, account, startId):
        crawler = Crawler()
        global currentCrawler
        # TODO: Bad asyn code, refine it later.
        currentCrawler = crawler
        try:
            crawler.init(account, self.dataBase)
            crawler.crawl(startId, 100)
            log.info("Crawler end.")
        except CrawlerException, e:
            log.info("Crawler end with exception, reason: " + str(e))
        finally:
            crawler.dispose()
        
def main():
    log.config(GC.LOG_FILE_DIR + 'crawler_test', 'info', 'info')
    signal.signal(signal.SIGINT, detectSignal)
    manager = CrawlManager()
    manager.startCrawling()

if __name__ == "__main__":
    main()
