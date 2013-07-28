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
from analyse.result import Result
from entities.name_helper import NameHelper
    

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

        self.accumulateXingMing(name, profile)

        # Set global info
        self.result.globalInfo.person_count += 1
        if profile.gender == Gender.MALE:
            self.result.globalInfo.male_count += 1
        elif profile.gender == Gender.FEMALE:
            self.result.globalInfo.female_count += 1


    def setInfo(self, info, profile):
        """Set the vars in info base on the profile."""
        info.count += 1
        if profile.gender == Gender.MALE:
            info.male_count += 1
        elif profile.gender == Gender.FEMALE:
            info.female_count += 1

    def accumulateXingChar(self, char, profile):
        """Accumulate a single char for Xing."""
        self.result.globalInfo.xing_char_count += 1
        info = self.result.xingCharMap.get(char)
        if not info:
            info = NameHelper.getInitedRawNameItemInfo(char)
            self.result.xingCharMap[char] = info
        self.setInfo(info, profile)

    
    def accumulateMingChar(self, char, profile):
        """Accumulate a single char for Name."""
        self.result.globalInfo.ming_char_count += 1
        info = self.result.mingCharMap.get(char)
        if not info:
            info = NameHelper.getInitedRawNameItemInfo(char)
            self.result.mingCharMap[char] = info
        self.setInfo(info, profile)
    
    def accumulateXing(self, xing, profile):
        """Accumulate a single Xing."""
        self.result.globalInfo.xing_count += 1
        info = self.result.xingMap.get(xing)
        if not info:
            info = NameHelper.getInitedRawNameItemInfo(xing)
            self.result.xingMap[xing] = info
        self.setInfo(info, profile)
    
    def accumulateMing(self, ming, profile):
        """Accumulate a single Name."""
        self.result.globalInfo.ming_count += 1
        info = self.result.mingMap.get(ming)
        if not info:
            info = NameHelper.getInitedRawNameItemInfo(ming)
            self.result.mingMap[ming] = info
        self.setInfo(info, profile)

    def accumulateXingMing(self, xingMing, profile):
        """Accumulate a single Name."""
        self.result.globalInfo.xing_ming_count += 1
        info = self.result.xingMingMap.get(xingMing)
        if not info:
            info = NameHelper.getInitedRawNameItemInfo(xingMing)
            self.result.xingMingMap[xingMing] = info
        self.setInfo(info, profile)

def main():
    analyser = Analyser()
    analyser.analyse()
    analyser.buildIndex()

if __name__ == "__main__":
    flag.processArguments()
    log.config(GC.LOG_FILE_DIR + 'Analyser', 'info', 'info')
    main()
