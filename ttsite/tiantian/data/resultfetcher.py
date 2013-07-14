#!/usr/bin/python
# -*- coding: utf-8 -*-

from tiantian.data.namedatabase import getNameDataBase


def getResultFetcher():
    return _resultFetcher


class ResultData:

    xingInfo = None
    mingInfo = None
    mingCharInfoList = None

    # Summary:
    maleRate = None
    femaleRate = None
    genderInfoValid = False


class ResultFetcher:
   
    def fetchData(self, xing, ming):
        nameDataBase = getNameDataBase()
        data = ResultData()
        data.xingInfo = nameDataBase.getXingInfo(xing)
        data.mingInfo = nameDataBase.getMingInfo(ming)
        data.mingCharInfoList = []
        for ch in ming:
          data.mingCharInfoList.append(nameDataBase.getMingCharInfo(ch))

        genderValidCount = 0
        maleRateSum = 0
        for info in data.mingCharInfoList:
            if info and info.genderInfoValid:
                genderValidCount += 1
                maleRateSum += info.maleRate

        if genderValidCount > 0:
            data.maleRate = maleRateSum / genderValidCount
            data.femaleRate = 1 - data.maleRate
            data.genderInfoValid = True

        return data


_resultFetcher = ResultFetcher()
