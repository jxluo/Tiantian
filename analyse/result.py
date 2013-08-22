#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import flag
from jx import log
from entities.name_pb2 import RawNameItemInfo, GlobalNameInfo
from entities.name_helper import NameHelper

from struct import *

flag.defineFlag('xing_char_map_min_count', flag.FlagType.INT, 2,\
    'item info with count smaller than this will be filtered out.')
flag.defineFlag('xing_map_min_count', flag.FlagType.INT, 2,\
    'item info with count smaller than this will be filtered out.')
flag.defineFlag('ming_char_map_min_count', flag.FlagType.INT, 2,\
    'item info with count smaller than this will be filtered out.')
flag.defineFlag('ming_map_min_count', flag.FlagType.INT, 5,\
    'item info with count smaller than this will be filtered out.')
flag.defineFlag('xing_ming_map_min_count', flag.FlagType.INT, 5,\
    'item info with count smaller than this will be filtered out.')


class Result:
    """Analysis result."""
    globalInfo = None

    xingCharMap = None # Family name character map object.
    xingCharSortedArray = None # A array contains sorted xing Char.
                               # Set by @caculate.

    xingMap = None # Family name string map object.
    xingSortedArray = None # A array contains sorted xing.
                           # Set by @caculate.

    mingCharMap = None # First name character map object.
    mingCharSortedArray = None # A array contains sorted ming char.
                               # Set by @caculate.
    
    mingMap = None # First name string map object.
    mingSortedArray = None # A array contains sorted ming.
                           # Set by @caculate.

    xingMingMap = None # Full name string map object.
    xingMingSortedArray = None # A array contains sorted full name.

    def __init__(self):
        self.globalInfo = NameHelper.getInitedGlobalNameInfo()
        self.xingCharMap = {} # Family name character map object.
        self.xingMap = {} # Family name string map object.
        self.mingCharMap = {} # First name character map object.
        self.mingMap = {} # First name string map object.
        self.xingMingMap = {} # Full name string map object.

    def filter(self):
        xingCharMapMinCount = flag.getFlag('xing_char_map_min_count')
        xingMapMinCount = flag.getFlag('xing_map_min_count')
        mingCharMapMinCount = flag.getFlag('ming_char_map_min_count')
        mingMapMinCount = flag.getFlag('ming_map_min_count')
        xingMingMapMinCount = flag.getFlag('xing_ming_map_min_count')

        log.info('==== Start filter, before: ====')
        log.info('Number of different xing:  %s' % len(self.xingMap))
        log.info('Number of different xing char:  %s' % len(self.xingCharMap))
        log.info('Number of different ming:  %s' % len(self.mingMap))
        log.info('Number of different ming char:  %s' % len(self.mingCharMap))
        log.info('Number of different xing ming:  %s' % len(self.xingMingMap))

        Result.filterMapOnThreshold(self.xingCharMap, xingCharMapMinCount)
        Result.filterMapOnThreshold(self.xingMap, xingMapMinCount)
        Result.filterMapOnThreshold(self.mingCharMap, mingCharMapMinCount)
        Result.filterMapOnThreshold(self.mingMap, mingMapMinCount)
        Result.filterMapOnThreshold(self.xingMingMap, xingMingMapMinCount)

        log.info('==== After filter: ====')
        log.info('Number of different xing:  %s' % len(self.xingMap))
        log.info('Number of different xing char:  %s' % len(self.xingCharMap))
        log.info('Number of different ming:  %s' % len(self.mingMap))
        log.info('Number of different ming char:  %s' % len(self.mingCharMap))
        log.info('Number of different xing ming:  %s' % len(self.xingMingMap))

    @staticmethod
    def filterMapOnThreshold(m, threshold):
        """Filter out the items in the map with count less than threshold.
        This function is optional when analysing.
        """
        if threshold < 2:
            return

        for item in m.items():
            info = item[1]
            if info.count < threshold:
                m.pop(item[0])
        

    def caculate(self):
        """Caculate detail information, such as rank.
        This fucntion is necessary when analysing. 
        """
        self.xingCharSortedArray = Result.caculateRank(self.xingCharMap)
        self.xingSortedArray = Result.caculateRank(self.xingMap)
        self.mingCharSortedArray = Result.caculateRank(self.mingCharMap)
        self.mingSortedArray = Result.caculateRank(self.mingMap)
        self.xingMingSortedArray = Result.caculateRank(self.xingMingMap)
        
        self.globalInfo.diff_xing_char_count = len(self.xingCharMap)
        self.globalInfo.diff_xing_count = len(self.xingMap)
        self.globalInfo.diff_ming_char_count = len(self.mingCharMap)
        self.globalInfo.diff_ming_count = len(self.mingMap)
        self.globalInfo.diff_xing_ming_count = len(self.xingMingMap)

    @staticmethod
    def caculateRank(m):
        """Caculate rank for a map."""
        infos = [item[1] for item in m.items()]
        infos.sort(key=lambda x: x.count, reverse=True)
        keys = []
        sumCount = 0
        for i in range(0, len(infos)):
            info = infos[i]
            sumCount += info.count
            info.sum_count = sumCount
            info.rank = i + 1
            keys.append(info.text)
        return keys

    def writeToFile(self, fileName):
        f = open(fileName, 'w')
        # Global infomation 4 * 3 = 12 bytes
        NameHelper.writeProtoToFile(f, self.globalInfo)

        # Write Map
        Result.writeMapToFile(f, self.xingCharMap)
        Result.writeMapToFile(f, self.xingMap)
        Result.writeMapToFile(f, self.mingCharMap)
        Result.writeMapToFile(f, self.mingMap)
        Result.writeMapToFile(f, self.xingMingMap)

        # Write array
        Result.writeArrayToFile(f, self.xingCharSortedArray)
        Result.writeArrayToFile(f, self.xingSortedArray)
        Result.writeArrayToFile(f, self.mingCharSortedArray)
        Result.writeArrayToFile(f, self.mingSortedArray)
        Result.writeArrayToFile(f, self.xingMingSortedArray)
        f.close()

    def readFromFile(self, fileName):
        f = open(fileName, 'r')
        # Global infomation
        self.globalInfo = NameHelper.readProtoFromFile(f, GlobalNameInfo)

        # Read Map
        self.xingCharMap = Result.readMapFromFile(f)
        self.xingMap = Result.readMapFromFile(f)
        self.mingCharMap = Result.readMapFromFile(f)
        self.mingMap = Result.readMapFromFile(f)
        self.xingMingMap = Result.readMapFromFile(f)

        # Read array
        self.xingCharSortedArray = Result.readArrayFromFile(f)
        self.xingSortedArray = Result.readArrayFromFile(f)
        self.mingCharSortedArray = Result.readArrayFromFile(f)
        self.mingSortedArray = Result.readArrayFromFile(f)
        self.xingMingSortedArray = Result.readArrayFromFile(f)
        f.close()

    @staticmethod
    def writeMapToFile(f, m):
        # Size of the map, 4 bytes
        buf = pack('<i', len(m))
        f.write(buf)
        for item in m.items():
            info = item[1]
            NameHelper.writeProtoToFile(f, info)
    
    @staticmethod
    def readMapFromFile(f):
        m = {}
        # Size of the map, 4 bytes
        buf = f.read(4)
        size, = unpack('<i', buf)
        for i in range(0, size):
            info = NameHelper.readProtoFromFile(f, RawNameItemInfo)
            assert not m.get(info.text), 'Duplicate key in the map.'
            m[info.text] = info
        return m

    @staticmethod
    def readMapFromFileGenerator(f):
        # Size of the map, 4 bytes
        buf = f.read(4)
        size, = unpack('<i', buf)
        for i in range(0, size):
            info = NameHelper.readProtoFromFile(f, RawNameItemInfo)
            yield info
    
    @staticmethod
    def writeArrayToFile(f, array):
        # Size of the array, 4 bytes
        buf = pack('<i', len(array))
        f.write(buf)
        for key in array:
            string = key.encode('utf-8');
            length = len(string)
            buf = pack('<i%ss' % length, length, string)
            f.write(buf)
    
    @staticmethod
    def readArrayFromFile(f):
        array = []
        # Size of the array, 4 bytes
        buf = f.read(4)
        lenOfArray, = unpack('<i', buf)
        for i in range(0, lenOfArray):
            buf = f.read(4)
            lenOfKey, = unpack('<i', buf)
            buf = f.read(lenOfKey)
            key = buf.decode('utf-8')
            array.append(key)
        return array
    
    @staticmethod
    def readArrayFromFileGenerator(f):
        # Size of the array, 4 bytes
        buf = f.read(4)
        lenOfArray, = unpack('<i', buf)
        for i in range(0, lenOfArray):
            buf = f.read(4)
            lenOfKey, = unpack('<i', buf)
            buf = f.read(lenOfKey)
            key = buf.decode('utf-8')
            yield (key, i)

    def readableWriteToFile(self, dirName):
        """Write readable result to file."""
        log.info('==== Write result files to directory: %s ====' % dirName)
        log.info('Number of xing:  %s' % self.globalInfo.xing_count)
        log.info('Number of different xing:  %s' %\
            self.globalInfo.diff_xing_count)
        log.info('Number of xing char:  %s' % self.globalInfo.xing_char_count)
        log.info('Number of different xing char:  %s' %\
            self.globalInfo.diff_xing_char_count)
        log.info('Number of ming:  %s' % self.globalInfo.ming_count)
        log.info('Number of different ming:  %s' % self.globalInfo.diff_ming_count)
        log.info('Number of ming char:  %s' % self.globalInfo.ming_char_count)
        log.info('Number of different ming char:  %s' %\
            self.globalInfo.diff_ming_char_count)
        log.info('Number of xing ming:  %s' % self.globalInfo.xing_ming_count)
        log.info('Number of different xing ming:  %s' %\
            self.globalInfo.diff_xing_ming_count)
        
        self.readableWriteMapToFile(
            self.xingMap, self.xingSortedArray, dirName + '/XingMap')
        self.readableWriteMapToFile(
            self.xingCharMap, self.xingCharSortedArray, dirName + '/XingCharMap')
        self.readableWriteMapToFile(
            self.mingMap, self.mingSortedArray, dirName + '/MingMap')
        self.readableWriteMapToFile(
            self.mingCharMap, self.mingCharSortedArray, dirName + '/MingCharMap')
        self.readableWriteMapToFile(
            self.xingMingMap, self.xingMingSortedArray, dirName + '/XingMingMap')


    def readableWriteMapToFile(self, m, a, fileName):
        f = open(fileName, 'w')
        infos = [m[key] for key in a]
        #values.sort(key=lambda x: x.count, reverse=True)
        f.write('Total: ' + str(len(infos)) + '\n')
        for info in infos:
            f.write(str(info.rank) + '\t')
            f.write(info.text.encode('utf-8') + '\t')
            f.write(str(info.count) + '\t')
            f.write(str(info.male_count) + '\t')
            f.write(str(info.female_count) + '\t')
            f.write('\n')
        f.close()
