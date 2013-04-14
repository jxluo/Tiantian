#!/usr/bin/python
#-*-coding:utf-8 -*-

import sys
sys.path.append('..')

import log
import globalconfig as GC
import confidential as CFD
from resourcepool import RenrenAccountPool
from resourcepool import createTestRenrenAccountPool
from resourcepool import createProdRenrenAccountPool


def main():
    log.config(GC.LOG_FILE_DIR + 'import_accounts', 'info', 'info')
    fileName = "accounts_from_github"
    importCount = 0
    failCount = 0
    #pool = createTestRenrenAccountPool()
    pool = createProdRenrenAccountPool()
    with open(fileName) as importedFile:
        lines = importedFile.readlines()
        for line in lines:
            strs = line.split()
            if len(strs) < 2:
                continue # May be not a valid account
            username = strs[0] # User name first.
            password = strs[1] # And then password.
            log.info("Importing username: " + username + "  " +\
                "password: " + password)
            success = pool.addAccount(username, password, fileName)
            if success:
                importCount += 1
            else:
                failCount += 1

    log.info("Finish importing..........\n" +\
        "Total imported accounts number: " +\
        str(importCount) + "\n" +\
        "Fail accounts number: " +\
        str(failCount))

if __name__ == "__main__":
  main()
