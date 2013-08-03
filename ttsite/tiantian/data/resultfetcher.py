#!/usr/bin/python
# -*- coding: utf-8 -*-

from tiantian.data.namedatabase import getNameDataBase
from entities.name_pb2 import NONE, LOW, HIGH

def getResultFetcher():
    return _resultFetcher


class ResultData:

    xingMingInfo= None
    xingInfo = None
    mingInfo = None
    mingCharInfoList = None

    estimatedMaleRate = None
    estimatedFemaleRate = None
    estimatedGenderReliable = NONE


class ResultFetcher:
   
    def fetchData(self, xingMing, xing, ming):
        nameDataBase = getNameDataBase()
        data = ResultData()
        data.xingMingInfo = nameDataBase.getXingMingInfo(xingMing)
        data.xingInfo = nameDataBase.getXingInfo(xing)
        data.mingInfo = nameDataBase.getMingInfo(ming)
        data.mingCharInfoList = []
        for ch in ming:
          data.mingCharInfoList.append(nameDataBase.getMingCharInfo(ch))

        # Caculate estimated gender info.
        genderValidCount = 0
        maleRateSum = 0
        for info in data.mingCharInfoList:
            if info and info.gender.reliable > NONE:
                genderValidCount += 1
                maleRateSum += info.gender.male_rate

        if genderValidCount > 0:
            data.estimatedMaleRate = maleRateSum / genderValidCount
            data.estimatedFemaleRate = 1 - data.estimatedMaleRate
            data.estimatedGenderReliable = LOW

        return data


_resultFetcher = ResultFetcher()
