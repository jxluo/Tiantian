#!/usr/bin/python
# -*- coding: utf-8 -*-

from entities.name_pb2 import GlobalNameInfo
from entities.name_pb2 import RawNameItemInfo

from struct import pack, unpack


class NameHelper:
    """ The helper class for name proto.
    """
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

