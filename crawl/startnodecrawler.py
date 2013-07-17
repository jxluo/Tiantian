#!/usr/bin/python
#-*-coding:utf-8 -*-

from jx import log
from utils import globalconfig as GC
from utils import util
from crawl.shareagent import ShareAgent, SharePageInfo
from resource.renrenaccount import RenrenAccount
from resource.renrenaccount import RenrenAccountErrorCode
from resource.renrenaccountpool import createProdRenrenAccountPool
from resource.renrenaccountpool import RenrenAccountPool
from data.database import createProdDataBase
from data.database import Status

import time

class StartNodeCrawler:

    tempFile = 'files/startshareurl'
    
    userList = None
    shareList = None
    
    def __init__(self, dataBase=None, accountPool=None):
        if dataBase:
            self.dataBase = dataBase
        else:
            self.dataBase = createProdDataBase()
        if accountPool:
            self.renrenAccountPool = accountPool
        else:
            self.renrenAccountPool = createProdRenrenAccountPool()
        
        self.dataBase.releaseAllStartNode()
        self.userList = []
        self.shareList = []

    def getAgentWithAccount(self):
        loginFailLimit = 5
        pool = self.renrenAccountPool
        loginFailAccounts = []

        account = None
        agent = None
        for i in range(0, loginFailLimit):
            account = pool.getAccount()
            if not account: 
                # No avaliable account in the database.
                break
            agent = ShareAgent(account)
            agent.login()
            time.sleep(1)
            if agent.isLogin:
                # Login success.
                break
            else:
                log.warning('Start node crawler login fail.')
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

    def expandSharePage(self, sharePageInfo, agent):
        for url in sharePageInfo.popularShareList:
            log.info('Share agent is crawling url: %s' % url)
            info = agent.getSharePageInfo(url)
            if info:
                for user in info.commentUserList:
                    self.addUser(user)
                for shareUrl in info.popularShareList:
                    self.shareList.append(shareUrl)
            time.sleep(1)

    def addUser(self, userId):
        if userId not in self.userList:
            self.userList.append(userId)

    def handleUserList(self):
        log.info('Finish crawling start nodes, total user number: %s' %\
            len(self.userList))
        for id in self.userList:
            status = self.dataBase.getStatus(id)
            if status != Status.expanded:
                # Inser into start list.
                self.dataBase.insertIntoStartList(id)
                log.info('Inser into start list: %s' % id)
            else:
                log.info('This id have been expanded: %s' % id)

    def startCrawling(self):
        """Crawl start nodes.
        Returns:
            True if success, otherwise False.
        """
        account = None
        try:
            url = self.getStartUrl()
            agent, account = self.getAgentWithAccount()
            if not agent:
                raise Exception('No account to crawl start nodes.')

            info = agent.getSharePageInfo(url)
            if not info:
                raise Exception('Get start share url fail.')
            time.sleep(0.8)

            self.expandSharePage(info, agent)
            self.handleUserList()
            # Update the new share url
            if self.shareList:
                self.writeStartUrl(self.shareList[-1])
            return True
        except Exception, e:
            log.warning('Crawl start node fail: %s' % str(e))
            return False
        finally:
            if account:
                account.finishUsing()

    def getStartUrl(self):
        f = open(self.tempFile)
        line = f.readline()
        while line == '\n':
            line = f.readline()
        
        assert line, 'No start url'
        if line[-1:] == '\n':
            line = line[:-1]
        return line
    

    def writeStartUrl(self, url):
        f = open(self.tempFile, 'w')
        f.write(url)
        f.close()

def main():
    log.config(GC.LOG_FILE_DIR + 'crawl_start_node', 'debug', 'debug')
    crawler = StartNodeCrawler()
    crawler.startCrawling()
    


if __name__ == '__main__':
    main()
