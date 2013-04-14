#!/usr/bin/python
# -*- coding: utf-8 -*-

import log
import globalconfig as GC
from crawler import Crawler
from crawler import CrawlerException
from crawler import CrawlerErrorCode
from renrenagent import UserInfo
from renrenagent import RenrenAgent
from database import UserNode
from database import DataBase
import database
import time
import threading

from databasetest import createConnection
from databasetest import createTables
from databasetest import dropTables

import resourcepool

import signal

crawler = None

def test():

    log.config(GC.LOG_FILE_DIR + 'crawler_test', 'info', 'info')
    db = createConnection()
    createTables(db)
    dropTables(db)
    createTables(db)

    pool = resourcepool.createProdRenrenAccountPool()
    accounts = pool.getAccounts(1)
    account = accounts[0]

    global crawler
    
    try:
        crawler = Crawler()
        crawler.init(account, db)
        id = "322601086"
        crawler.crawl(id, 30)
    except CrawlerException, e:
        log.info("Crawler end, reason: " + str(e))
    finally:
        print "finally"
        crawler.dispose()

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
