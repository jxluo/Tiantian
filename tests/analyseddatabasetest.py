#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import log
from utils import globalconfig as GC
from analyse.result import MapValue
from analyse.result import Result
from sitedata.analyseddatabase import AnalysedDataBase
from sitedata.analyseddatabase import createTestAnalysedDataBase
from tests.util import getRandomResult, assertValueEqual


def getAllValue(m):
    return [item[1] for item in m.items()]

def assertArrayMatch(array, rank, neighbors):
    count = 7
    start = rank - count / 2
    if start < 1: start = 1
    for i in range(0, len(neighbors)):
        assert array[start + i - 1] == neighbors[i]
    

def testAanlysedDataBase():
    wdb = createTestAnalysedDataBase()
    #result = getRandomResult(10)
    result = getRandomResult()
    wdb.importResult(result)
    wdb.close()

    rdb = createTestAnalysedDataBase()
    
    # Test global info
    rdb.readGlobalInfo()
    assert rdb.allXingCharCount == result.allXingCharCount
    assert rdb.allXingCount == result.allXingCount
    assert rdb.allMingCharCount == result.allMingCharCount
    assert rdb.allMingCount == result.allMingCount
    assert rdb.personCount == result.personCount
    assert rdb.maleCount == result.globalMaleCount
    assert rdb.femaleCount == result.globalFemaleCount

    # Test Map
    for value in getAllValue(result.xingCharMap):
        newValue = rdb.getXingCharMap(value.key)
        assertValueEqual(value, newValue)
    for value in getAllValue(result.xingMap):
        newValue = rdb.getXingMap(value.key)
        assertValueEqual(value, newValue)
    for value in getAllValue(result.mingCharMap):
        newValue = rdb.getMingCharMap(value.key)
        assertValueEqual(value, newValue)
    for value in getAllValue(result.mingMap):
        newValue = rdb.getMingMap(value.key)
        assertValueEqual(value, newValue)

    # Test Array
    for i in range(1, len(result.xingCharSortedArray) + 1):
        neighbors = rdb.getXingCharRankNeighbors(i)
        assertArrayMatch(result.xingCharSortedArray, i, neighbors)
    for i in range(1, len(result.xingSortedArray) + 1):
        neighbors = rdb.getXingRankNeighbors(i)
        assertArrayMatch(result.xingSortedArray, i, neighbors)
    for i in range(1, len(result.mingCharSortedArray) + 1):
        neighbors = rdb.getMingCharRankNeighbors(i)
        assertArrayMatch(result.mingCharSortedArray, i, neighbors)
    for i in range(1, len(result.mingSortedArray) + 1):
        neighbors = rdb.getMingRankNeighbors(i)
        assertArrayMatch(result.mingSortedArray, i, neighbors)


    log.info("Pass the test!")






def main():
    log.config(GC.LOG_FILE_DIR + 'analysed_data_base_test', 'debug', 'debug')
    testAanlysedDataBase()

if __name__ == "__main__":
  main();
