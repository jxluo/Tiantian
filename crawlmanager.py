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
from resourcepool import RenrenAccountErrorCode
from proxypool import createProdProxyPool
from resourcepool import RenrenAccountPool

from crawler import Crawler
from crawler import CrawlerException
from crawler import CrawlerErrorCode
from proxy import Proxy
from renrenagent import RenrenAgent

import threading
import router

currentCrawler = None
stopSignal = False

def detectSignal(a, b):
    print "INT Signal detect"
    Crawler.setStopSignal()


class CrawlThread(threading.Thread):
    """A single crawling thread."""
    threadId = 0
    dataBase = None
    renrenAccountPool = None
    proxy = None

    accountUsed = 0
    # limit 
    ACCOUNTS_LIMIT = 10
    FAIL_LOGIN_ACCOUNT_LIMIT = 5

    THREAD_ID_COUNT = 0
    THREAD_ID_COUNT_LOCK = threading.RLock()

    def getThreadId(self):
        CrawlThread.THREAD_ID_COUNT_LOCK.acquire()
        threadId = CrawlThread.THREAD_ID_COUNT
        CrawlThread.THREAD_ID_COUNT += 1
        CrawlThread.THREAD_ID_COUNT_LOCK.release()
        return threadId


    def __init__(self, dataBase, pool, proxy=None):
        threading.Thread.__init__(self)
        self.threadId = self.getThreadId()
        log.info('>>>>>>  Create thread %s.  <<<<<<' % self.threadId)
        self.dataBase = dataBase
        self.renrenAccountPool = pool
        self.proxy = proxy

    def getAgentWithAccount(self):
        loginFailLimit = self.FAIL_LOGIN_ACCOUNT_LIMIT
        pool = self.renrenAccountPool
        loginFailAccounts = []

        account = None
        agent = None
        for i in range(0, loginFailLimit):
            if self.accountUsed >= self.ACCOUNTS_LIMIT:
                # Run out of accounts credit.
                break
            self.accountUsed += 1
            account = pool.getAccount()
            if not account: 
                # No avaliable account in the database.
                break
            agent = RenrenAgent(account, self.proxy)
            agent.login()
            time.sleep(1)
            if agent.isLogin:
                # Login success.
                break
            else:
                log.warning('Thread %s login fail.' % self.threadId)
                loginFailAccounts.append(account)

        if agent and agent.isLogin:
            for account in loginFailAccounts:
                account.reportInvalidAccount(RenrenAccountErrorCode.ERROR_WHEN_LOGIN)
            return agent, account
        else:
            for account in loginFailAccounts:
                #account.finishUsing()
                account.reportInvalidAccount(RenrenAccountErrorCode.ERROR_WHEN_LOGIN)
            # TODO: Find a better way.
            return None, None

    def run(self):
        log.info('>>>>>>  Thread %s start.  <<<<<<' % self.threadId)
        crawler = Crawler(self.dataBase)
        dataBase = self.dataBase
        agent = None
        account = None
        startNode = None
        startNodeRowId = None
        try:
            while True:
                # Prepare for agent, account and startnode.
                if not agent or not account:
                    agent,account = self.getAgentWithAccount()
                    if not agent or not account:
                        # No avaliable account, exit crawling.
                        log.warning(
                            'No avaliable agent for thread %s, exit crawling.' %\
                            (self.threadId, ))
                        break
                if not startNode:
                    startNode, startNodeRowId = dataBase.getStartNode()
                    log.info('Thread %s, startnode: %s, %s' %\
                        (self.threadId, startNode, startNodeRowId))
                    if not startNode or not startNodeRowId:
                        # No avaliable start node, exit crawling.
                        log.error(
                            'No start node for thread %s, exit crawling.' %\
                            (self.threadId, ))
                        break

                # One crawling process.
                crawler.setAgent(agent)
                try:
                    crawler.crawl(startNode)
                except CrawlerException, e:
                    log.info('Thread %s gets exception: %s' %\
                        (self.threadId, str(e)))
                    if e.errorCode == CrawlerErrorCode.DETECT_STOP_SIGNAL:
                        log.info("Thread " + str(self.threadId) +\
                            " stop crawling because of stop signal.")
                        break
                    if e.errorCode ==\
                        CrawlerErrorCode.GET_EXPANDING_NODE_FAILED or\
                        e.errorCode == CrawlerErrorCode.EXPAND_EXPANDED_NODE or\
                        e.errorCode == CrawlerErrorCode.NO_NODE_TO_EXPAND:
                        # Start node's bad.
                        log.warning('Thread %s, bad start node: %s, %s' %\
                            (self.threadId, startNode, startNodeRowId))
                        dataBase.deleteFromStartList(startNode)
                        startNode = startNodeRowId = None
                    if e.errorCode == CrawlerErrorCode.REQUEST_FAILED:
                        # Still start node's bad.
                        # TODO: Implement invalid usernode test support in
                        # database to change it.
                        log.warning('Thread %s, bad start node: %s, %s' %\
                            (self.threadId, startNode, startNodeRowId))
                        dataBase.deleteFromStartList(startNode)
                        startNode = startNodeRowId = None
                    if e.errorCode == CrawlerErrorCode.REACH_REQUEST_LIMIT:
                        # Use a new accout
                        account.finishUsing()
                        account = agent = None
                finally:
                    # The start node change every time crawler.epand() called.
                    # So the start node can not be reused when exception happen.
                    # We need to release it and use a new one.
                    if startNodeRowId:
                        dataBase.releaseStartNode(startNodeRowId)
                        startNode = startNodeRowId = None
        except Exception, e:
            log.error('Thread %s gets exception, exit crawling: %s' %\
                (self.threadId, str(e)))
        finally:
            # Release resource.
            if account:
                account.finishUsing()
            if startNodeRowId:
                dataBase.releaseStartNode(startNodeRowId)
        log.info('>>>>>>  Thread %s end.  <<<<<<' % self.threadId)

class MainCrawlThread(threading.Thread):

    dataBase = None
    renrenAccountPool = None

    crawlRound = 30

    def __init__(self):
        threading.Thread.__init__(self)

    def startMultiThreadCrawling(self, threadNumber):
        self.dataBase = createProdDataBase()
        self.dataBase.releaseAllStartNode()
        self.renrenAccountPool = createProdRenrenAccountPool()

        threads = []
        for i in range(0, threadNumber):
            thread = CrawlThread(self.dataBase, self.renrenAccountPool)
            threads.append(thread)
            thread.start()
            time.sleep(1.5)

        for thread in threads:
            thread.join()

    def startSignleThreadCrawling(self):
        self.dataBase = createProdDataBase()
        self.dataBase.releaseAllStartNode()
        self.renrenAccountPool = createProdRenrenAccountPool()
        thread = CrawlThread(self.dataBase, self.renrenAccountPool)
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
                self.dataBase, self.renrenAccountPool, proxies[i])
            threads.append(thread)
            thread.start()
            time.sleep(1.5)

        for thread in threads:
            thread.join()

    def run(self):
        for i in range(0, self.crawlRound):
            log.info('>>>>>>>>  Main Crawl Thread Round(%s)  <<<<<<<<' % (i+1))
            self.startMultiThreadCrawling(8)
            #self.startMultiThreadCrawlingWithProxy(1)
            #manager.startSignleThreadCrawling()

            try:
                Crawler.detectStopSignal()
            except Exception, e:
                break

            log.info('>>>>>> Router disconnect PPPoE  <<<<<<')
            router.disconnectPPPoE()
            time.sleep(2)
            log.info('>>>>>> Router connect PPPoE  <<<<<<')
            router.connectPPPoE()
            # Wait for the connection being established.
            time.sleep(10)

class CrawlManager:
     
    def start(self):
        thread = MainCrawlThread()
        thread.start()
        
        # Wait for a signal
        signal.pause()
        thread.join()
        log.info(">>>>>>>>>>  Main thread end....  <<<<<<<<<<")




        
def main():
    log.config(GC.LOG_FILE_DIR + 'CrawlManager', 'info', 'info')
    signal.signal(signal.SIGINT, detectSignal)
    manager = CrawlManager()
    manager.start()

if __name__ == "__main__":
    main()
