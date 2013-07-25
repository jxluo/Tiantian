#!/usr/bin/python
# -*- coding: utf-8 -*-

from analyse.result import MapValue
from sitedata.analyseddatabase import GlobalInfo

class InfoReliability:
    """Enum of reliability"""
    (UNRELIABLE, # Unreliable
     LOW, # Row reliability
     HIGH # High reliability
     ) = range(0, 3)


class GenderInfo:
    
    maleRate = None # The rate of male
    femaleRate = None # The rate of female
    reliability = None

    # Reliability Threshold
    ENOUGH_COUNT = 100

    @staticmethod
    def getInfo(maleCount, femaleCount, globalInfo):
        """
        PM : The posibility for a male contained in database.
        PF : The posibility for a female contained in database.
        We assume that PM / PF = globalMaleCount / globalFemaleCount
        maleRate = maleCount * PF / (maleCount * PF + femaleCount * PM)
        femaleRate = femaleCount * PM / (maleCount * PF + femaleCount * PM)
        """
        #print '========'
        #print maleCount, femaleCount, globalInfo.maleCount, globalInfo.femaleCount
        info = GenderInfo()

        if not maleCount and not femaleCount:
            info.reliability = InfoReliability.UNRELIABLE
            return info

        PFM = float(globalInfo.femaleCount) / globalInfo.maleCount
        t = float(maleCount) * PFM
        info.maleRate = t / (t + femaleCount)

        PMF = float(globalInfo.maleCount) / globalInfo.femaleCount
        t = float(femaleCount) * PMF
        info.femaleRate = t / (t + maleCount)

        totalCount = maleCount + femaleCount
        if totalCount > GenderInfo.ENOUGH_COUNT:
            info.reliability = InfoReliability.HIGH
        else:
            info.reliability = InfoReliability.LOW

        #print info.maleRate, info.femaleRate
        #print info.maleRate + info.femaleRate

        return info


class Info:
    """The statistic information for a xing or ming, or ming char. """

    text = None # The text string of ming or xing or ming char.
    rank = None
    genderInfo = None


    # Raw information
    maleCount = None
    femaleCount = None
    count = None


    @staticmethod
    def fromValue(value, globalInfo):
        if not value:
            return None

        info = Info()
        
        info.text = value.key
        info.rank = value.rank
        # Gender
        info.genderInfo = GenderInfo.getInfo(\
            value.maleCount, value.femaleCount, globalInfo)
        
        # Raw info
        info.maleCount = value.maleCount
        info.femaleCount = value.femaleCount
        info.count = value.count

        return info
    




