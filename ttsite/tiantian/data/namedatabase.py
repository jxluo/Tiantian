#!/usr/bin/python
# -*- coding: utf-8 -*-

from sitedata.analyseddatabase import createProdAnalysedDataBase
from entities.name_pb2 import RawNameItemInfo, NameItemInfo, GlobalNameInfo
from entities.name_helper import NameHelper

print '############################################################'
print '#################  Load Name Data Base  ####################'
print '############################################################'

_analysedDataBase = createProdAnalysedDataBase()

def getNameDataBase():
    return _nameDataBase

class NameDataBase:
    

    _dataBase = None
    _globalInfo = _analysedDataBase.getGlobalInfo()
    
    def __init__(self):
        global _analysedDataBase
        self._dataBase = _analysedDataBase
    
    def getXingMingInfo(self, xingMing):
        """Get XingMing info, None if does not exist."""
        rawInfo = self._dataBase.getXingMingInfo(xingMing)
        if not rawInfo: return None
        globalInfo = self._dataBase.getGlobalInfo()
        return NameHelper.getXingMingInfo(rawInfo, globalInfo)

    def getXingInfo(self, xing):
        """Get Xing info, None if does not exist."""
        rawInfo = self._dataBase.getXingInfo(xing)
        if not rawInfo: return None
        globalInfo = self._dataBase.getGlobalInfo()
        return NameHelper.getXingInfo(rawInfo, globalInfo)

    def getMingInfo(self, ming):
        """Get Ming info, None if does not exist."""
        rawInfo = self._dataBase.getMingInfo(ming)
        if not rawInfo: return None
        globalInfo = self._dataBase.getGlobalInfo()
        return NameHelper.getMingInfo(rawInfo, globalInfo)

    def getMingCharInfo(self, mingChar):
        """Get MingChar info, None if does not exist."""
        rawInfo = self._dataBase.getMingCharInfo(mingChar)
        if not rawInfo: return None
        globalInfo = self._dataBase.getGlobalInfo()
        return NameHelper.getMingCharInfo(rawInfo, globalInfo)


_nameDataBase = NameDataBase()
