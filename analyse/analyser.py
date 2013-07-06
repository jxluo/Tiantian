#!/usr/bin/python
# -*- coding: utf-8 -*-

from jx import log
from jx import flag
from utils.util import isHanChar
from utils import confidential as CFD
from utils import globalconfig as GC
from data.database import Profile
from data.database import Gender
from data.readonlydatastore import createProdReadOnlyDataStore
from data.readonlydatastore import ReadOnlyDataStore
from analyse.result import MapValue
from analyse.result import Result
    

flag.defineFlag('use_result_filter', flag.FlagType.BOOLEAN, True,\
    'Whether there is need to filter some unnecessary content in result.')

def valueCmp(x, y):
    return x[1].count < y[1].count

class Analyser:
    """Analysis the data in data store and build the index of the result."""

    dataStore = None # The data source.
    result = Result()

    def __init__(self):
        self.dataStore = createProdReadOnlyDataStore()

    def analyse(self):
        """Analyse the data."""
        profiles = self.getProfiles()
        log.info('Total Profile number:  %s' % len(profiles))
        self.processProfiles(profiles)
        if flag.getFlag('use_result_filter'):
            self.result.filter()
        self.result.caculate()


    def buildIndex(self):
        self.result.readableWriteToFile('files')
        self.result.writeToFile('files/serialized_result')

    def getProfiles(self):
        """Get a list of profiles from the data store."""
        #profiles = self.dataStore.getAllProfiles()
        allProfiles = []
        while True:
            profiles = self.dataStore.get100KProfiles()
            if profiles:
                allProfiles.extend(profiles)
            else:
                break
        return filter(ReadOnlyDataStore.hasValidName, allProfiles)

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

        # Set global info
        self.result.personCount += 1
        if profile.gender == Gender.MALE:
            self.result.globalMaleCount += 1
        elif profile.gender == Gender.FEMALE:
            self.result.globalFemaleCount += 1


    def setValue(self, value, profile):
        """Set the vars in value base on the profile."""
        value.count += 1
        if profile.gender == Gender.MALE:
            value.maleCount += 1
        elif profile.gender == Gender.FEMALE:
            value.femaleCount += 1

    def accumulateXingChar(self, char, profile):
        """Accumulate a single char for Xing."""
        self.result.allXingCharCount += 1
        value = self.result.xingCharMap.get(char)
        if not value:
            value = MapValue(char, ord(char))
            self.result.xingCharMap[char] = value
        self.setValue(value, profile)

    
    def accumulateMingChar(self, char, profile):
        """Accumulate a single char for Name."""
        self.result.allMingCharCount += 1
        value = self.result.mingCharMap.get(char)
        if not value:
            value = MapValue(char, ord(char))
            self.result.mingCharMap[char] = value
        self.setValue(value, profile)
    
    def accumulateXing(self, xing, profile):
        """Accumulate a single Xing."""
        self.result.allXingCount += 1
        value = self.result.xingMap.get(xing)
        if not value:
            value = MapValue(xing, None)
            self.result.xingMap[xing] = value
        self.setValue(value, profile)
    
    def accumulateMing(self, ming, profile):
        """Accumulate a single Name."""
        self.result.allMingCount += 1
        value = self.result.mingMap.get(ming)
        if not value:
            value = MapValue(ming, None)
            self.result.mingMap[ming] = value
        self.setValue(value, profile)

def main():
    analyser = Analyser()
    analyser.analyse()
    analyser.buildIndex()

if __name__ == "__main__":
    flag.processArguments()
    log.config(GC.LOG_FILE_DIR + 'Analyser', 'info', 'info')
    main()
