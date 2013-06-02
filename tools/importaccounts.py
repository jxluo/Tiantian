#!/usr/bin/python
#-*-coding:utf-8 -*-

import sys
sys.path.append('..')

from jx import log
from jx.threadpool import ThreadPool
from utils import globalconfig as GC
from utils import confidential as CFD
from utils import router
from resource.renrenaccount import RenrenAccount
from resource.renrenaccountpool import RenrenAccountPool
from resource.renrenaccountpool import createTestRenrenAccountPool
from resource.renrenaccountpool import createProdRenrenAccountPool
from crawl.renrenagent import RenrenAgent

import time
import threading

importSuccessCount = 0
importFailCount = 0

verifySuccessCount = 0
verifyFailCount = 0

lock = threading.RLock()

    
class RenrenAccountVerifier:
    
    account = None
    callback = None #some class have method like:
                          # callback(self, account, success):
    success = None

    def __init__(self, account, callback=None):
        self.account = account
        self.callback = callback
        
    def verify(self):
        
        agent = RenrenAgent(self.account)
        agent.login()
        if agent.isLogin:
            self.success = True
        else:
            self.success = False
        log.info('Account Verify result: (%s, %s)  >>>  %s' %\
            (self.account.username, self.account.password, self.success))

        global lock
        global verifySuccessCount
        global verifyFailCount

        lock.acquire()
        if self.success:
            verifySuccessCount += 1
        else:
            verifyFailCount += 1
        lock.release()

    def handleResult(self):
        if self.callback:
            self.callback.callback(self.account, self.success)

    def run(self):
        self.verify()
        self.handleResult()

class VerifyCallback:

    pool = None
    fileName = None
    lock = threading.RLock()
    failFile = None

    def __init__(self, pool, fileName, failFile):
        self.pool = pool
        self.fileName = fileName
        self.failFile = failFile

    def handleFail(self, account):
        self.lock.acquire()
        string = '%s------%s\n' % (account.username, account.password)
        self.failFile.write(string)
        self.lock.release()
    
    def callback(self, account, success):
        if success:
            importSuccess = self.pool.addAccount(
                account.username, account.password, self.fileName)

            global lock
            global importSuccessCount
            global importFailCount
            lock.acquire()
            if importSuccess:
                importSuccessCount += 1
            else:
                importFailCount += 1
            lock.release()
        else:
            self.handleFail(account)


def importFromFile(fname):
    log.config(GC.LOG_FILE_DIR + 'import_accounts', 'info', 'info')
    fileName = fname
    accounts = []
    pool = createProdRenrenAccountPool()

    with open(fileName) as importedFile:
        lines = importedFile.readlines()
        for line in lines:
            strs = line.split()
            if len(strs) < 2:
                continue # May be not a valid account
            username = strs[0] # User name first.
            password = strs[1] # And then password.
            log.info("Find username: " + username + "  " +\
                "password: " + password)
            account = RenrenAccount(username, password, None)
            accounts.append(account)

    accountNumInOneRound = 10
    failFile = open('tools/data/verify_fail', 'w')
    callback = VerifyCallback(pool, fileName, failFile)
    while accounts:
        threadPool = ThreadPool(5)
        verifiers = []
        for i in range(0, accountNumInOneRound):
            if not accounts:
                break;
            verifier = RenrenAccountVerifier(accounts.pop(0), callback) 
            verifiers.append(verifier)
        if verifiers:
            threadPool.setStartInterval(1.2)
            threadPool.setTaskInterval(0.8)
            threadPool.start(verifiers)
            log.info('>>>>>> Router disconnect PPPoE  <<<<<<')
            router.disconnectPPPoE()
            time.sleep(2)
            log.info('>>>>>> Router connect PPPoE  <<<<<<')
            router.connectPPPoE()
            # Wait for the connection being established.
            time.sleep(5)

    failFile.close()

    log.info("Finish importing..........\n" +\
        "Success on verify accounts number: " +\
        str(verifySuccessCount) + "\n" +\
        "Fail on verify accounts number: " +\
        str(verifyFailCount))
    log.info('Success imported number: %s' % importSuccessCount)
    log.info('Fail imported number: %s' % importFailCount)

def main():
    importFromFile('tools/data/accounts_for_test')
    #importFromFile('accounts_from_taobao_yongji')
    #importFromFile('accounts_from_taobao_wanglihong')
    #importFromFile('accounts_from_taobao_wanglihong2')

if __name__ == "__main__":
  main()
