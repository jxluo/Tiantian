#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import log
from utils import globalconfig as GC
from analyse.result import Result
from tests.util import getRandomResult

import random


fileForResultTest = 'tmp/resulttest'
dirForResultTest = 'tmp'


def assertMapEqual(a, b):
    assert len(a) == len(b)
    akeys = [item[0] for item in a.items()]
    bkeys = [item[0] for item in b.items()]
    assert len(akeys) == len(bkeys)
    for key in akeys:
        ainfo = a.get(key)
        binfo = b.get(key)
        ainfo == binfo

def assertArrayEqual(a, b):
    assert len(a) == len(b)
    for i in range(0, len(a)):
        assert a[i] == b[i]

def assertResultEqual(a, b):
    # Global information:
    a.globalInfo == b.globalInfo

    # Map
    assertMapEqual(a.xingCharMap, b.xingCharMap)
    assertMapEqual(a.xingMap, b.xingMap)
    assertMapEqual(a.mingCharMap, b.mingCharMap)
    assertMapEqual(a.mingMap, b.mingMap)
    assertMapEqual(a.xingMingMap, b.xingMingMap)

    # Array
    assertArrayEqual(a.xingCharSortedArray, b.xingCharSortedArray)
    assertArrayEqual(a.xingSortedArray, b.xingSortedArray)
    assertArrayEqual(a.mingCharSortedArray, b.mingCharSortedArray)
    assertArrayEqual(a.mingSortedArray, b.mingSortedArray)
    assertArrayEqual(a.xingMingSortedArray, b.xingMingSortedArray)

def assertMapArrayMatch(m, a):
    for i in range(0, len(a)):
        if i > 0:
            key1 = a[i-1]
            key2 = a[i]
            info1 = m[key1]
            info1.text == key1
            info2 = m[key2]
            info2.text == key2
            assert info1.count >= info2.count

def testResultSerialization():
    result = getRandomResult()

    assertMapArrayMatch(result.xingCharMap, result.xingCharSortedArray)
    assertMapArrayMatch(result.xingMap, result.xingSortedArray)
    assertMapArrayMatch(result.mingCharMap, result.mingCharSortedArray)
    assertMapArrayMatch(result.mingMap, result.mingSortedArray)
    assertMapArrayMatch(result.xingMingMap, result.xingMingSortedArray)

    result.writeToFile(fileForResultTest)

    newResult = Result()
    newResult.readFromFile(fileForResultTest)
    assertResultEqual(result, newResult)

    result.readableWriteToFile(dirForResultTest)


def main():
    log.config(GC.LOG_FILE_DIR + 'result_test', 'debug', 'debug')
    testResultSerialization()
    log.info("Pass the test!")

if __name__ == "__main__":
  main();





