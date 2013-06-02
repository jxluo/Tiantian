#!/usr/bin/python
#-*-coding:utf-8 -*-

import sys
sys.path.append('..')

from jx import log
from utils import globalconfig as GC
from utils import confidential as CFD
from data import database


def main():
    log.config(GC.LOG_FILE_DIR + 'import_start_nodes', 'info', 'info')
    fileName = "tools/data/start_nodes"
    importCount = 0
    failCount = 0
    dataBase = database.createProdDataBase()
    with open(fileName) as importedFile:
        lines = importedFile.readlines()
        for line in lines:
            strs = line.split()
            if len(strs) < 1:
                continue # May be not a valid account
            id = strs[0] # Start node id.
            log.info("Importing start node: " + id)
            success = dataBase.insertIntoStartList(id)
            if success:
                importCount += 1
            else:
                failCount += 1

    log.info("Finish importing..........\n" +\
        "Total imported start nodes number: " +\
        str(importCount) + "\n" +\
        "Fail start nodes number: " +\
        str(failCount))

if __name__ == "__main__":
  main()
