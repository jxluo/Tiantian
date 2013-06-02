#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import log
from utils.util import isHanChar
from utils import confidential as CFD
from utils import globalconfig as GC
from data.database import Profile
from data.database import Gender
from data.readonlydatastore import createProdReadOnlyDataStore
from data.readonlydatastore import ReadOnlyDataStore


class MapValue:
    key = None # The key, it's a char or string.
    code = None # The unicode value of the key if the key is a char.

    count = 0 # How many times it appear.
    maleCount = 0 # How many male have this char in his name.
    femaleCount = 0 # How many female have this char in her name.
    
    def __init__(self, key, code):
        self.key = key
        self.code = code
    
def valueCmp(x, y):
    return x[1].count < y[1].count

class Analyser:
    """Analysis the data in data store and build the index of the result."""

    allXingCharCount = 0
    xingCharMap = {} # Family name character map object.

    allXingCount = 0
    xingMap = {} # Family name string map object.

    allMingCharCount = 0
    mingCharMap = {} # First name character map object.
    
    allMingCount = 0
    mingMap = {} # First name string map object.

    dataStore = None # The data source.

    def __init__(self):
        self.dataStore = createProdReadOnlyDataStore()

    def analyse(self):
        """Analyse the data."""
        profiles = self.getProfiles()
        print 'Profile number:  ' + str(len(profiles))
        self.processProfiles(profiles)




    def writeMapToFile(self, m, fname):
        f = open(fname, 'w')
        values = [item[1] for item in m.items()]
        values.sort(key=lambda x: x.count, reverse=True)
        print 'Total: ' + str(len(values))
        f.write('Total: ' + str(len(values)) + '\n')
        for value in values:
            f.write(value.key.encode('utf-8') + '\t')
            if value.code: f.write(str(value.code) + '\t')
            f.write(str(value.count) + '\t')
            f.write(str(value.maleCount) + '\t')
            f.write(str(value.femaleCount) + '\t')
            if value.femaleCount > 1:
                f.write(str(float(value.maleCount) / value.femaleCount) + '\t')
            f.write('\n')
        f.close()

    def buildIndex(self):
        """Build  the index with the result."""
        print 'All Xing:  ' + str(self.allXingCount)
        print 'All Xing Char:  ' + str(self.allXingCharCount)
        print 'All Ming:  ' + str(self.allMingCount)
        print 'All Ming Char:  ' + str(self.allMingCharCount)
        self.writeMapToFile(self.xingMap, 'tmp/XingMap')
        self.writeMapToFile(self.xingCharMap, 'tmp/XingCharMap')
        self.writeMapToFile(self.mingMap, 'tmp/MingMap')
        self.writeMapToFile(self.mingCharMap, 'tmp/MingCharMap')

    def getProfiles(self):
        """Get a list of profiles from the data store."""
        profiles = self.dataStore.getAllProfiles()
        return filter(ReadOnlyDataStore.hasValidName, profiles)

    def processProfiles(self, profiles):
        """Process a list of profiles."""
        for profile in profiles:
            self.accumulate(profile)

    def accumulate(self, profile):
        """Accumulate a single profile."""
        name = profile.name
        if not 2 <= len(name) <= 4:
            return
        if len(name) == 4:
            xing = name[:2]
            ming = name[2:]
        else:
            xing = name[:1]
            ming = name[1:]

        self.accumulateXing(xing, profile)
        for char in xing:
            self.accumulateXingChar(char, profile)

        self.accumulateMing(ming, profile)
        for char in ming:
            self.accumulateMingChar(char, profile)


    def setValue(self, value, profile):
        """Set the vars in value base on the profile."""
        value.count += 1
        if profile.gender == Gender.MALE:
            value.maleCount += 1
        elif profile.gender == Gender.FEMALE:
            value.femaleCount += 1

    def accumulateXingChar(self, char, profile):
        """Accumulate a single char for Xing."""
        self.allXingCharCount += 1
        value = self.xingCharMap.get(char)
        if not value:
            value = MapValue(char, ord(char))
            self.xingCharMap[char] = value
        self.setValue(value, profile)

    
    def accumulateMingChar(self, char, profile):
        """Accumulate a single char for Name."""
        self.allMingCharCount += 1
        value = self.mingCharMap.get(char)
        if not value:
            value = MapValue(char, ord(char))
            self.mingCharMap[char] = value
        self.setValue(value, profile)
    
    def accumulateXing(self, xing, profile):
        """Accumulate a single Xing."""
        self.allXingCount += 1
        value = self.xingMap.get(xing)
        if not value:
            value = MapValue(xing, None)
            self.xingMap[xing] = value
        self.setValue(value, profile)
    
    def accumulateMing(self, ming, profile):
        """Accumulate a single Name."""
        self.allMingCount += 1
        value = self.mingMap.get(ming)
        if not value:
            value = MapValue(ming, None)
            self.mingMap[ming] = value
        self.setValue(value, profile)

def main():
    analyser = Analyser()
    analyser.analyse()
    analyser.buildIndex()

main()
