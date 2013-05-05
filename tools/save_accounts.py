#!/usr/bin/python
#-*-coding:utf-8 -*-

import sys
sys.path.append('..')
import log
import time
import globalconfig as GC
import confidential as CFD
from resourcepool import createProdRenrenAccountPool
from renrenagent import RenrenAgent

def saveInUsingAccounts(pool):
    getAllUsingAccountsCommand = """
        SELECT username, password FROM RenrenAccounts
        WHERE is_using = 1 AND
            is_valid = 1 AND
            last_used_time <= DATE_SUB(NOW(), INTERVAL 1 DAY)
        ORDER BY last_used_time ASC;
    """
    pool.cursor.execute(getAllUsingAccountsCommand)
    rows = pool.cursor.fetchall()
    log.info('Total InUsing account:' + str(len(rows)))
    for row in rows:
        pool.saveAccount(row[0], row[1], True, '1971-1-1')


def saveInvalidAccount(pool):
    command = """
        SELECT username, password FROM RenrenAccounts
        WHERE is_valid = 0
        ORDER BY last_used_time DESC;
    """
    pool.cursor.execute(command)
    rows = pool.cursor.fetchall()
    log.info('Total InValid account:' + str(len(rows)))
    failCount = 0

    for row in rows:
        username = row[0]
        password = row[1]
        saveSuccess = False
        if pool.onceSaveFail(username, password):
            continue
        if failCount > 100:
            break;
        try:
            time.sleep(2)
            agent = RenrenAgent(username, password)
            agent.login()
            saveSuccess = agent.isLogin
        except Exception, e:
            log.warning('Save login fail:  ' + str(e))
        finally:
            log.info('Save Invalid account(' + username + ', ' + password +\
                '):   ' + str(saveSuccess))
            if saveSuccess:
                failCount = 0
            else:
                failCount += 1
            pool.saveAccount(username, password, saveSuccess)


def main():
    log.config(GC.LOG_FILE_DIR + 'save_accounts', 'info', 'info')
    pool = createProdRenrenAccountPool()
    saveInUsingAccounts(pool)
    saveInvalidAccount(pool)


main()
