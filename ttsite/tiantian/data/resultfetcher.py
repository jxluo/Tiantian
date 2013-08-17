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

    summaryMaleRate = None
    summaryFemaleRate = None
    hasGenderInfo = None

    summarySumRate = None


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

        xmInfo = data.xingMingInfo
        xInfo = data.xingInfo
        mInfo = data.mingInfo
        mcInfos = data.mingCharInfoList
        
        # Caculate summary gender info.
        if xmInfo and xmInfo.gender.reliable == HIGH:
            data.summaryMaleRate = xmInfo.gender.male_rate
            data.summaryFemaleRate = xmInfo.gender.female_rate
            data.hasGenderInfo = True
        elif mInfo and mInfo.gender.reliable == HIGH:
            data.summaryMaleRate = mInfo.gender.male_rate
            data.summaryFemaleRate = mInfo.gender.female_rate
            data.hasGenderInfo = True
        else:
            genderValidCount = 0
            maleRateSum = 0
            for info in mcInfos:
                if info and info.gender.reliable > NONE:
                    genderValidCount += 1
                    maleRateSum += info.gender.male_rate

            if genderValidCount > 0:
                data.summaryMaleRate = maleRateSum / genderValidCount
                data.summaryFemaleRate = 1 - data.summaryMaleRate 
                data.hasGenderInfo = True

        #Caculate summary sum rate
        data.summarySumRate = 2
        if xmInfo:
            data.summarySumRate = xmInfo.sum_rate
        elif mInfo and xInfo:
            data.summarySumRate = (xInfo.sum_rate + mInfo.sum_rate) / 2

        return data


_resultFetcher = ResultFetcher()
