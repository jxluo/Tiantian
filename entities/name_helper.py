#!/usr/bin/python
# -*- coding: utf-8 -*-

from entities.name_pb2 import GlobalNameInfo
from entities.name_pb2 import RawNameItemInfo
from entities.name_pb2 import NameItemInfo
from entities.name_pb2 import GenderInfo
from entities.name_pb2 import NONE, LOW, HIGH

from struct import pack, unpack


class NameHelper:
    """ The helper class for name proto.
    """

    ENOUGH_COUNT_FOR_GENDER = 10
    ENOUGH_COUNT_FOR_ITEM = 100
    
    @staticmethod
    def getInitedNameItemInfo():
        info = NameItemInfo()
        info.text = ''
        info.reliable = NONE
        info.rate = 0
        info.rank = -1
        info.rank_rate = 0
        info.sum_rate = 0
        return info
    
    @staticmethod
    def getInitedGenderInfo():
        info = GenderInfo()
        info.reliable = NONE
        info.male_rate = 0
        info.female_rate = 0
        return info

    @staticmethod
    def getInitedRawNameItemInfo(text):
        """ Returns a defualt initialized RawNameItemInfo instance."""
        info = RawNameItemInfo()
        info.text = text
        info.count = 0
        info.male_count = 0
        info.female_count = 0
        info.rank = -1
        info.sum_count = -1
        return info
    
    @staticmethod
    def getInitedGlobalNameInfo():
        """ Returns a defualt initialized GlobalNameInfo instance."""
        info = GlobalNameInfo()
        info.xing_char_count = 0;
        info.diff_xing_char_count = 0;

        info.xing_count = 0;
        info.diff_xing_count = 0;

        info.ming_char_count = 0;
        info.diff_ming_char_count =0;

        info.ming_count = 0;
        info.diff_ming_count = 0;

        info.xing_ming_count = 0;
        info.diff_xing_ming_count = 0;

        info.person_count = 0;
        info.male_count = 0;
        info.female_count = 0;

        return info

    @staticmethod
    def writeProtoToFile(f, proto):
        """Write a proto to file."""
        s = proto.SerializeToString()
        l = len(s)
        buf = pack('<i%ss' % l, l, s)
        f.write(buf)

    @staticmethod
    def readProtoFromFile(f, ProtoClass):
        """Read a proto from file, it should be written by WriteProtoToFile."""
        buf = f.read(4)
        l, = unpack('<i', buf)
        s = f.read(l)
        proto = ProtoClass.FromString(s)
        return proto

    @staticmethod
    def getGenderInfo(rawInfo, globalInfo):
        return NameHelper._getGenderInfo(\
            rawInfo.male_count, rawInfo.female_count, globalInfo)

    @staticmethod
    def _getGenderInfo(maleCount, femaleCount, globalInfo):
        """
        PM : The posibility for a male contained in database.
        PF : The posibility for a female contained in database.
        We assume that PM / PF = globalMaleCount / globalFemaleCount
        maleRate = maleCount * PF / (maleCount * PF + femaleCount * PM)
        femaleRate = femaleCount * PM / (maleCount * PF + femaleCount * PM)
        """
        info = NameHelper.getInitedGenderInfo()

        if not maleCount and not femaleCount:
            info.reliable = NONE
            return info

        PFM = float(globalInfo.female_count) / globalInfo.male_count
        t = float(maleCount) * PFM
        info.male_rate = t / (t + femaleCount)

        PMF = float(globalInfo.male_count) / globalInfo.female_count
        t = float(femaleCount) * PMF
        info.female_rate = t / (t + maleCount)

        totalCount = maleCount + femaleCount
        if totalCount > NameHelper.ENOUGH_COUNT_FOR_GENDER:
            info.reliable = HIGH
        else:
            info.reliable = LOW

        #print info.maleRate, info.femaleRate
        #print info.maleRate + info.femaleRate
        return info
    
    @staticmethod
    def getXingInfo(rawInfo, globalInfo):
        return NameHelper._getNameItemInfo(rawInfo, globalInfo,\
            globalInfo.xing_count, globalInfo.diff_xing_count)

    @staticmethod
    def getXingCharInfo(rawInfo, globalInfo):
        return NameHelper._getNameItemInfo(rawInfo, globalInfo,\
            globalInfo.xing_char_count, globalInfo.diff_xing_char_count)

    @staticmethod
    def getMingInfo(rawInfo, globalInfo):
        return NameHelper._getNameItemInfo(rawInfo, globalInfo,\
            globalInfo.ming_count, globalInfo.diff_ming_count)

    @staticmethod
    def getMingCharInfo(rawInfo, globalInfo):
        return NameHelper._getNameItemInfo(rawInfo, globalInfo,\
            globalInfo.ming_char_count, globalInfo.diff_ming_char_count)

    @staticmethod
    def getXingMingInfo(rawInfo, globalInfo):
        return NameHelper._getNameItemInfo(rawInfo, globalInfo,\
            globalInfo.xing_ming_count, globalInfo.diff_xing_ming_count)

    @staticmethod
    def _getNameItemInfo(rawInfo, globalInfo, total_count, diff_count):
        info = NameHelper.getInitedNameItemInfo()
        info.text = rawInfo.text
        info.reliable =\
            HIGH if rawInfo.count > NameHelper.ENOUGH_COUNT_FOR_ITEM else LOW
        info.rate = float(rawInfo.count)/ total_count
        info.rank = rawInfo.rank
        info.rank_rate = float(rawInfo.rank) / diff_count
        info.sum_rate = float(rawInfo.sum_count) / total_count
        
        # Gender
        info.gender.CopyFrom(NameHelper.getGenderInfo(rawInfo, globalInfo))
        # Raw info
        info.raw_info.CopyFrom(rawInfo)
        return info
