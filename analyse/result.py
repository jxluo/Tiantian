#!/usr/bin/python
# -*- coding: utf-8 -*-

from struct import *

class MapValue:
    key = None # The key, it's a char or string.
    code = None # The unicode value of the key if the key is a char.

    count = 0 # How many times it appear.
    maleCount = 0 # How many male have this char in his name.
    femaleCount = 0 # How many female have this char in her name.
    #TODO: location info.

    rank = None # The count rank, from high to low. Set in @caculate
    
    def __init__(self, key=None, code=None):
        self.key = key
        self.code = code

    def serialize(self):
        """Serialize the object to a string and return."""
        string = ''
        # Key length and key sring, 4 + x bytes
        keyString = self.key.encode('utf-8')
        lenOfKey = len(keyString)
        buf = pack('<i%ss' % lenOfKey, lenOfKey, keyString)
        string = string + buf

        # Code 4 bytes, If there is no code, write a 0
        codeToWrite = 0
        if self.code: codeToWrite = self.code
        buf = pack('<i', codeToWrite)
        string = string + buf

        # The count, male count, female count 4 * 3 = 12 bytes
        buf = pack('<3i', self.count, self.maleCount, self.femaleCount)
        string = string + buf
        
        # The rank 4 bytes
        buf = pack('<i', self.rank)
        string = string + buf

        return string

    def cut(self, string, length):
        buf = string[:length]
        newString = string[length:]
        return buf, newString
   
    def unserialize(self, string):
        """Construct the object from a string."""
        # Key length and key sring, 4 + x bytes
        buf, string = self.cut(string, 4)
        lenOfKey, = unpack('<i', buf)
        buf, string = self.cut(string, lenOfKey)
        keyString, = unpack('<%ss' % lenOfKey, buf)
        self.key = keyString.decode('utf-8')

        # Code 4 bytes, If there is no code, it will be 0
        buf, string = self.cut(string, 4)
        codeReaded, = unpack('<i', buf)
        if codeReaded:
            self.code = codeReaded
        else:
            self.code = None

        # The count, male count, female count 4 * 3 = 12 bytes
        buf, string = self.cut(string, 12)
        self.count, self.maleCount, self.femaleCount = unpack('<3i', buf)
        
        # The rank 4 bytes
        buf, string = self.cut(string, 4)
        self.rank, = unpack('<i', buf)

    def write(self, f):
        string = self.serialize()
        lenOfStr = len(string)
        # The length of the serialized string, 4 bytes.
        # The serialized string.
        buf = pack('<i%ss' % lenOfStr, lenOfStr, string)
        f.write(buf)

    def read(self, f):
        # String length and serialized sring, 4 + x bytes
        buf = f.read(4)
        lenOfStr, = unpack('<i', buf)
        buf = f.read(lenOfStr)
        string, = unpack('<%ss' % lenOfStr, buf)
        self.unserialize(string)

class Result:
    """Analysis result."""
    allXingCharCount = 0
    xingCharMap = {} # Family name character map object.
    xingCharSortedArray = None # A array contains sorted xing Char.
                               # Set by @caculate.

    allXingCount = 0
    xingMap = {} # Family name string map object.
    xingSortedArray = None # A array contains sorted xing.
                           # Set by @caculate.

    allMingCharCount = 0
    mingCharMap = {} # First name character map object.
    mingCharSortedArray = None # A array contains sorted ming char.
                               # Set by @caculate.
    
    allMingCount = 0
    mingMap = {} # First name string map object.
    mingSortedArray = None # A array contains sorted ming.
                           # Set by @caculate.

    personCount = 0 # Number of person in this result.
    globalMaleCount = 0 # Number of male in global scope.
    globalFemaleCount = 0 # Number of female in global scope.
    # TODO: global location count

    def caculate(self):
        """Caculate detail information, such as rank."""
        self.xingCharSortedArray = Result.caculateRank(self.xingCharMap)
        self.xingSortedArray = Result.caculateRank(self.xingMap)
        self.mingCharSortedArray = Result.caculateRank(self.mingCharMap)
        self.mingSortedArray = Result.caculateRank(self.mingMap)

    @staticmethod
    def caculateRank(m):
        """Caculate rank for a map."""
        values = [item[1] for item in m.items()]
        values.sort(key=lambda x: x.count, reverse=True)
        keys = []
        for i in range(0, len(values)):
            value = values[i]
            value.rank = i + 1
            keys.append(value.key)
        return keys

    def writeToFile(self, fileName):
        f = open(fileName, 'w')
        # Global infomation 4 * 3 = 12 bytes
        buf = pack('<3i',\
            self.personCount, self.globalMaleCount, self.globalFemaleCount)
        f.write(buf)
        
        # MapCount 4 * 4 = 16 bytes
        buf = pack('<4i',\
            self.allXingCharCount, self.allXingCount,\
            self.allMingCharCount, self.allMingCount)
        f.write(buf)

        # Write Map
        Result.writeMapToFile(f, self.xingCharMap)
        Result.writeMapToFile(f, self.xingMap)
        Result.writeMapToFile(f, self.mingCharMap)
        Result.writeMapToFile(f, self.mingMap)

        # Write array
        Result.writeArrayToFile(f, self.xingCharSortedArray)
        Result.writeArrayToFile(f, self.xingSortedArray)
        Result.writeArrayToFile(f, self.mingCharSortedArray)
        Result.writeArrayToFile(f, self.mingSortedArray)
        f.close()

    def readFromFile(self, fileName):
        f = open(fileName, 'r')
        # Global infomation 4 * 3 = 12 bytes
        buf = f.read(12)
        self.personCount, self.globalMaleCount, self.globalFemaleCount =\
            unpack('<3i', buf)
        
        # MapCount 4 * 4 = 16 bytes
        buf = f.read(16)
        self.allXingCharCount, self.allXingCount,\
            self.allMingCharCount, self.allMingCount = unpack('<4i', buf)

        # Read Map
        self.xingCharMap = Result.readMapFromFile(f)
        self.xingMap = Result.readMapFromFile(f)
        self.mingCharMap = Result.readMapFromFile(f)
        self.mingMap = Result.readMapFromFile(f)

        # Read array
        self.xingCharSortedArray = Result.readArrayFromFile(f)
        self.xingSortedArray = Result.readArrayFromFile(f)
        self.mingCharSortedArray = Result.readArrayFromFile(f)
        self.mingSortedArray = Result.readArrayFromFile(f)
        f.close()

    @staticmethod
    def writeMapToFile(f, m):
        # Size of the map, 4 bytes
        buf = pack('<i', len(m))
        f.write(buf)
        for item in m.items():
            value = item[1]
            value.write(f)
    
    @staticmethod
    def readMapFromFile(f):
        m = {}
        # Size of the map, 4 bytes
        buf = f.read(4)
        size, = unpack('<i', buf)
        for i in range(0, size):
            value = MapValue()
            value.read(f)
            assert not m.get(value.key), 'Duplicate key in the map.'
            m[value.key] = value
        return m
    
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

    def readableWriteToFile(self, dirName):
        """Write readable result to file."""
        print 'All Xing:  ' + str(self.allXingCount)
        print 'All Xing Char:  ' + str(self.allXingCharCount)
        print 'All Ming:  ' + str(self.allMingCount)
        print 'All Ming Char:  ' + str(self.allMingCharCount)
        self.readableWriteMapToFile(
            self.xingMap, self.xingSortedArray, 'tmp/XingMap')
        self.readableWriteMapToFile(
            self.xingCharMap, self.xingCharSortedArray, 'tmp/XingCharMap')
        self.readableWriteMapToFile(
            self.mingMap, self.mingSortedArray, 'tmp/MingMap')
        self.readableWriteMapToFile(
            self.mingCharMap, self.mingCharSortedArray, 'tmp/MingCharMap')


    def readableWriteMapToFile(self, m, a, fileName):
        f = open(fileName, 'w')
        values = [m[key] for key in a]
        #values.sort(key=lambda x: x.count, reverse=True)
        print 'Total: ' + str(len(values))
        f.write('Total: ' + str(len(values)) + '\n')
        for value in values:
            f.write(value.key.encode('utf-8') + '\t')
            #if value.code: f.write(str(value.code) + '\t')
            f.write(str(value.count) + '\t')
            f.write(str(value.maleCount) + '\t')
            f.write(str(value.femaleCount) + '\t')
            if value.femaleCount > 1:
                f.write(str(float(value.maleCount) / value.femaleCount) + '\t')
            f.write('\n')
        f.close()
