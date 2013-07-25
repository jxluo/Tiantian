#!/usr/bin/python
# -*- coding: utf-8 -*-

from tiantian.data.namedatabase import getNameDataBase
from tiantian.data.info import InfoReliability


def getResultFetcher():
    return _resultFetcher


class ResultData:

    xingInfo = None
    mingInfo = None

    mingCharInfoList = None
    estimatedMaleRate = None
    estimatedFemaleRate = None
    estimatedGenderReliability = InfoReliability.UNRELIABLE


class ResultFetcher:
   
    def fetchData(self, xing, ming):
        nameDataBase = getNameDataBase()
        data = ResultData()
        data.xingInfo = nameDataBase.getXingInfo(xing)
        data.mingInfo = nameDataBase.getMingInfo(ming)
        data.mingCharInfoList = []
        for ch in ming:
          data.mingCharInfoList.append(nameDataBase.getMingCharInfo(ch))

        # Caculate estimated gender info.
        genderValidCount = 0
        maleRateSum = 0
        for info in data.mingCharInfoList:
            if info and info.genderInfo.reliability:
                genderValidCount += 1
                maleRateSum += info.genderInfo.maleRate

        if genderValidCount > 0:
            data.estimatedMaleRate = maleRateSum / genderValidCount
            data.estimatedFemaleRate = 1 - data.estimatedMaleRate
            data.estimatedGenderReliability = InfoReliability.LOW

        return data


_resultFetcher = ResultFetcher()
