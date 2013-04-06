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

def test():

    log.config(GC.LOG_FILE_DIR + 'crawler_test', 'debug', 'debug')
    db = createConnection()
    createTables(db)
    dropTables(db)
    createTables(db)
    agent = RenrenAgent('zhanglini.ok@163.com', '12345678')
    agent.login()
    
    crawler = Crawler(agent, db)
    id = "322601086"
    crawler.crawl(id, 10)


def main():
    test()

if __name__ == "__main__":
    main()
