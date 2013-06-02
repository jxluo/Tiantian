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


def test(dataStore):
    profiles = dataStore.getAllProfiles()
    print 'All profiles: ' + str(len(profiles))
    validCount = 0
    invalidCount = 0
    f_valid = open('allprofiles_valid.txt', 'w')
    f_invalid = open('allprofiles_invalid.txt', 'w')
    for profile in profiles:
        if ReadOnlyDataStore.hasValidName(profile):
            f_valid.write(profile.id.encode('utf-8') + '\t')
            f_valid.write(profile.name.encode('utf-8') + '\n')
            validCount += 1
        else:
            f_invalid.write(profile.id.encode('utf-8') + '\t')
            f_invalid.write(profile.name.encode('utf-8') + '\t')
            for char in profile.name:
                if not isHanChar(char):
                    f_invalid.write(char.encode('utf-8'))
            f_invalid.write('\n')
            invalidCount += 1

    f_valid.close()
    f_invalid.close()
    print 'valid: ' + str(validCount)
    print 'invalid: ' + str(invalidCount)


def main():
    log.config(GC.LOG_FILE_DIR + 'readonlydatastore_test', 'debug', 'debug')
    dataStore = createProdReadOnlyDataStore()
    test(dataStore)
    dataStore.close()


main()
