#!/usr/bin/python
# -*- coding: utf-8 -*-

import log
import globalconfig as GC
import confidential as CFD
from resourcepool import RenrenAccount
from resourcepool import RenrenAccountLogEvent
from resourcepool import RenrenAccountErrorCode
from resourcepool import RenrenAccountPool

from proxy import Proxy
from proxypool import createTestProxyPool

def createPool():
    pool = RenrenAccountPool()
    pool.init(CFD.TEST_HOST,
        CFD.TEST_USER_NAME,
        CFD.TEST_PWD,
        CFD.TEST_DATA_BASE);
    return pool

def createTables(db):
    with open('resourceschema.sql') as script:
        lines = script.readlines()
        command = ''
        for i in range(0, len(lines)):
            line = lines[i]
            command += line
            #print line
            if line.find(';') != -1:
                #print "================="
                db.cursor.execute(command) 
                db.mdbConnection.commit()
                command = ''

def dropTables(db):
    script = "DROP TABLE RenrenAccounts;"
    db.cursor.execute(script) 
    db.mdbConnection.commit()
    script = "DROP TABLE RenrenAccountsLog;"
    db.cursor.execute(script) 
    db.mdbConnection.commit()
    script = "DROP TABLE Proxies;"
    db.cursor.execute(script) 
    db.mdbConnection.commit()

def test(pool):
    usn1 = "username_1"
    pwd1 = "password_1"
    usn2 = "username_2"
    pwd2 = "password_2"
    usn3 = "username_3"
    pwd3 = "password_3"
    usn4 = "username_4"
    pwd4 = "password_4"
    comeFrom = "from test."

    pool.addAccount(usn1, pwd1, comeFrom)
    pool.addAccount(usn2, pwd2, comeFrom)
    pool.addAccount(usn3, pwd3, comeFrom)
    pool.addAccount(usn4, pwd4, comeFrom)

    # Test get 0
    accounts = pool.getAccounts(0)
    assert len(accounts) == 0

    # Test get part of the accounts
    accounts = pool.getAccounts(2)
    assert len(accounts) == 2
    for account in accounts:
        account.finishUsing()

    # Test get all of the accounts
    accounts = pool.getAccounts(10)
    assert len(accounts) == 4
    for account in accounts:
        account.finishUsing()

    # Test finish using.
    accounts = pool.getAccounts(10)
    assert len(accounts) == 4
    accounts[0].isLogin = True
    accounts[0].requestCount = 30
    for account in accounts:
        account.finishUsing()

    accounts = pool.getAccounts(10)
    assert len(accounts) == 3

    # Test report invalid
    accounts[0].isLogin = True
    accounts[0].requestCount = 30
    accounts[0].reportInvalidAccount(RenrenAccountErrorCode.ERROR_WHEN_REQUEST)
    accounts[1].reportInvalidAccount(RenrenAccountErrorCode.ERROR_WHEN_LOGIN)
    accounts[2].finishUsing()

    invalidAccount1 = accounts[0]
    invalidAccount2 = accounts[1]

    accounts = pool.getAccounts(10)
    assert len(accounts) == 1

    # Test no available account
    accounts[0].isLogin = True
    accounts[0].requestCount = 60
    accounts[0].finishUsing()

    accounts = pool.getAccounts(10)
    assert len(accounts) == 0

    # Test save account
    pool.saveAccount(invalidAccount1.username, invalidAccount1.password, True,
        '1971-1-1')
    accounts = pool.getAccounts(10)
    assert len(accounts) == 1
    for account in accounts:
        account.finishUsing()
    
    # Test save account
    pool.saveAccount(invalidAccount2.username, invalidAccount2.password, False)
    accounts = pool.getAccounts(10)
    assert len(accounts) == 1
    for account in accounts:
        account.finishUsing()
    
    # Test save account
    pool.saveAccount(invalidAccount2.username, invalidAccount2.password, True)
    accounts = pool.getAccounts(10)
    assert len(accounts) == 1
    for account in accounts:
        account.finishUsing()

    assert pool.onceSaveFail(
        invalidAccount1.username, invalidAccount1.password) == False
    assert pool.onceSaveFail(
        invalidAccount2.username, invalidAccount2.password) == True

def assertProxyEqual(p1, p2):
    #print p1.addr
    #print p2.addr
    assert p1.addr == p2.addr
    assert p1.port == p2.port
    assert p1.protocol == p2.protocol or not p1.protocol or not p2.protocol
    assert p1.info == p2.info
    assert p1.source == p2.source
    assert p1.testCount == p2.testCount
    assert p1.successCount == p2.successCount
    assert p1.averageTime == p2.averageTime

def testProxyPool():
    proxy1 = Proxy()
    proxy1.addr = u'1.1.1.1'
    proxy1.port = u'1'
    proxy1.protocol = u'HTTP'
    proxy1.info = u'1234'
    proxy1.source = u'3321' 
    proxy1.testCount = 5
    proxy1.successCount = 5
    proxy1.averageTime = 20
    
    proxy2 = Proxy()
    proxy2.addr = u'2.2.2.2'
    proxy2.port = u'2'
    proxy2.protocol = u'SOCKET'
    proxy2.info = u'信息'
    proxy2.source = u'来源' 
    proxy2.testCount = 5
    proxy2.successCount = 5
    proxy2.averageTime = 200
    
    proxy3 = Proxy()
    proxy3.addr = u'3.3.3.3'
    proxy3.port = u'3'
    proxy3.protocol = None
    proxy3.info = None
    proxy3.source = None 
    proxy3.testCount = 5
    proxy3.successCount = 3
    proxy3.averageTime = 12000
    
    proxy4 = Proxy()
    proxy4.addr = u'4.4.4.4'
    proxy4.port = u'4'
    proxy4.protocol = u'HTTP'
    proxy4.info = None
    proxy4.source = None 

    pool = createTestProxyPool()

    assert len(pool.getAllProxies()) == 0
    pool.insertProxy(proxy1)
    pool.insertProxy(proxy2)
    pool.insertProxy(proxy3)
    pool.insertProxy(proxy4)
    assert len(pool.getAllProxies()) == 4

    proxies = pool.getProxies(2)
    assert len(proxies) == 2
    assertProxyEqual(proxies[0], proxy1)
    assertProxyEqual(proxies[1], proxy2)

    proxies = pool.getProxies(4)
    assert len(proxies) == 3
    assertProxyEqual(proxies[0], proxy1)
    assertProxyEqual(proxies[1], proxy2)
    assertProxyEqual(proxies[2], proxy3)

    proxy3.averageTime = 100
    pool.updateProxy(proxy3)
    proxies = pool.getProxies(4)
    assert len(proxies) == 3
    assertProxyEqual(proxies[0], proxy1)
    assertProxyEqual(proxies[1], proxy3)
    assertProxyEqual(proxies[2], proxy2)

    pool.deleteProxy(proxy1)
    assert len(pool.getAllProxies()) == 3
    pool.deleteAllProxies()
    assert len(pool.getAllProxies()) == 0

    pool.close()

def main():
    log.config(GC.LOG_FILE_DIR + 'account_pool_test', 'debug', 'debug')
    pool = createPool()
    createTables(pool)
    dropTables(pool)
    createTables(pool)
    test(pool)
    testProxyPool()
    dropTables(pool)
    pool.close()
    log.info("Pass the test!")

if __name__ == "__main__":
  main();
