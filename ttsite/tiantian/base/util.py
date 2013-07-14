#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils.util import isHanChar



def isValidName(name):
    """Is the string represent a valid name.
    
    Arguments:
        name: a name string, should be a python 'u' string.

    Return: True if it's a valid name.
    """
    lenOfName = len(name)
    if lenOfName < 2 or lenOfName > 4:
        return False

    for ch in name:
        if not isHanChar(ch):
            return False

    return True


def parseName(name):
    """Parse the name to (xing, ming).

    
    Arguments:
        name: a name string, should be a python 'u' string.

    Return:
        (Xing, Ming) if the name is a valid name.
        None if the name is not a valid name.
    """
    if not isValidName(name):
        return None

    if len(name) > 3:
        xing = name[:2]
        ming = name[2:]
    else:
        xing = name[:1]
        ming = name[1:]
    return (xing, ming)
        
