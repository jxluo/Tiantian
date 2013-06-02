#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import log
from utils import globalconfig as GC
from crawl.crawler import Crawler
from crawl.crawler import CrawlerException
from crawl.crawler import CrawlerErrorCode
from crawl.renrenagent import UserInfo
from crawl.renrenagent import RenrenAgent
from data.database import UserNode
from data.database import DataBase
from resource import renrenaccountpool
from tests.databasetest import createConnection
from tests.databasetest import createTables
from tests.databasetest import dropTables

import time
import threading
import signal

crawler = None

def test():

    log.config(GC.LOG_FILE_DIR + 'crawler_test', 'info', 'info')
    db = createConnection()
    createTables(db)
    dropTables(db)
    createTables(db)

    pool = renrenaccountpool.createProdRenrenAccountPool()
    accounts = pool.getAccounts(1)
    account = accounts[0]

    global crawler
    
    try:
        crawler = Crawler(db)
        agent = RenrenAgent(account)
        agent.login()
        crawler.setAgent(agent)
        id = "322601086"
        crawler.crawl(id, 30)
    except CrawlerException, e:
        log.info("Crawler end, reason: " + str(e))
        if e.errorCode == CrawlerErrorCode.DETECT_STOP_SIGNAL:
            print "detect int signal"
            return
    finally:
        print "finally"
        account.dispose()

def detectSignal(a, b):
    print "Signal detect"
    global crawler
    if crawler:
        crawler.setStopSignal()

def main():
    signal.signal(signal.SIGINT, detectSignal)
    test()

if __name__ == "__main__":
    main()
