#!/usr/bin/python
# -*- coding: utf-8 -*-

import log
import globalconfig as GC
import confidential as CFD
from resourcepool import RenrenAccount
from resourcepool import RenrenAccountLogEvent
from resourcepool import RenrenAccountErrorCode
from resourcepool import RenrenAccountPool


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

    accounts = pool.getAccounts(10)
    assert len(accounts) == 1

    # Test no available account
    accounts[0].isLogin = True
    accounts[0].requestCount = 60
    accounts[0].finishUsing()

    accounts = pool.getAccounts(10)
    assert len(accounts) == 0

def main():
    log.config(GC.LOG_FILE_DIR + 'account_pool_test', 'debug', 'debug')
    pool = createPool()
    createTables(pool)
    dropTables(pool)
    createTables(pool)
    test(pool)
    #dropTables(pool)
    pool.close()
    log.info("Pass the test!")

if __name__ == "__main__":
  main();
