#!/usr/bin/python
# -*- coding: utf-8 -*-

from analyse.result import MapValue


class Info:
    """The statistic information for a xing or ming, or ming char. """

    text = None # The text string of ming or xing or ming char.

    rank = None

    maleRate = None
    femaleRate = None

    maleCount = None
    femaleCount = None
    count = None

    genderInfoValid = False # Is gender infomation valid.
                            # (Have enough gender infomation)

    @staticmethod
    def fromValue(value):
        if not value:
            return None

        info = Info()
        info.text = value.key
        info.rank = value.rank
        info.maleCount = value.maleCount
        info.femaleCount = value.femaleCount
        info.count = value.count

        genderCount = value.maleCount + value.femaleCount
        if genderCount > 0:
            info.genderInfoValid = True
            info.maleRate = float(value.maleCount) / genderCount
            info.femaleRate = float(value.femaleCount) / genderCount
        else:
            info.genderInfoValid = False

        return info
    




