#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import log
from jx import flag
from jx.flag import FlagType
from utils import globalconfig as GC
from utils import router
from data.database import createProdDataBase
from resource.renrenaccount import RenrenAccountErrorCode
from resource.renrenaccountpool import createProdRenrenAccountPool
from resource.renrenaccountpool import RenrenAccountPool
from resource.proxypool import createProdProxyPool
from resource.proxy import Proxy
from crawl.crawler import Crawler
from crawl.crawler import CrawlerException
from crawl.crawler import CrawlerErrorCode
from crawl.renrenagent import RenrenAgent

import time
import threading
import signal

flag.defineFlag(name='waiting_time', type_=FlagType.INT, default=0,\
    description='Wait before crawling to let account become avaliable.(In mins)')

flag.defineFlag(name='accounts_limit', type_=FlagType.INT, default=10,\
    description='Account limit in a single thread.')
flag.defineFlag(name='thread_number', type_=FlagType.INT, default=8,\
    description='Crawling thread number in a single round.')
flag.defineFlag(name='round_number', type_=FlagType.INT, default=30,\
    description='Crawling round number.')

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
    ACCOUNTS_LIMIT = flag.getFlag('accounts_limit')
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
                account.finishUsing()
                #account.reportInvalidAccount(RenrenAccountErrorCode.ERROR_WHEN_LOGIN)
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
                if not agent or not account:
                    agent,account = self.getAgentWithAccount()
                    if not agent or not account:
                        # No avaliable account, exit crawling.
                        log.warning(
                            'No avaliable agent for thread %s, exit crawling.' %\
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

    THREAD_NUMBER = flag.getFlag('thread_number')
    ROUND_NUMBER = flag.getFlag('round_number')

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
        for i in range(0, self.ROUND_NUMBER):
            log.info('>>>>>>>>  Main Crawl Thread Round(%s)  <<<<<<<<' % (i+1))
            self.startMultiThreadCrawling(self.THREAD_NUMBER)
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
    flag.processArguments()
    log.config(GC.LOG_FILE_DIR + 'CrawlManager', 'info', 'info')
    signal.signal(signal.SIGINT, detectSignal)
    waitingTime = flag.getFlag('waiting_time')
    log.info('Wait for: ' + str(waitingTime) + ' minutes')
    time.sleep(waitingTime * 60)
    manager = CrawlManager()
    manager.start()

if __name__ == "__main__":
    main()
