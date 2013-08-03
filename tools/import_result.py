#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import log
from utils import globalconfig as GC
from analyse.result import Result
from sitedata.analyseddatabase import AnalysedDataBase
from sitedata.analyseddatabase import createTestAnalysedDataBase


def importResultToDataBase():
    result = Result()
    result.readFromFile('files/serialized_result')
    wdb = createTestAnalysedDataBase()
    wdb.importResult(result)
    wdb.close()
    log.info("Import finish!")


def main():
    log.config(GC.LOG_FILE_DIR + 'import_result_to_database', 'info', 'info')
    importResultToDataBase()

if __name__ == "__main__":
  main();
