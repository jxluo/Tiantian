#!/usr/bin/python
# -*- coding: utf-8 -*-

from sitedata.analyseddatabase import createTestAnalysedDataBase
from tiantian.data.info import Info


print '############################################################'
print '#################  Load Name Data Base  ####################'
print '############################################################'

_analysedDataBase = createTestAnalysedDataBase()

def getNameDataBase():
    return _nameDataBase

class NameDataBase:
    
    _dataBase = None
    
    def __init__(self):
        global _analysedDataBase
        self._dataBase = _analysedDataBase

    def getXingInfo(self, xing):
        value = self._dataBase.getXingMap(xing)
        return Info.fromValue(value)

    def getMingInfo(self, ming):
        value = self._dataBase.getMingMap(ming)
        return Info.fromValue(value)

    def getMingCharInfo(self, mingChar):
        value = self._dataBase.getMingCharMap(mingChar)
        return Info.fromValue(value)


_nameDataBase = NameDataBase()
