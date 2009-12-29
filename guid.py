#!/usr/bin/env python
#-*- coding: utf-8 -*-

from uuid import UUID as uuid_UUID

class UUID(uuid_UUID):
    def __init__(self, bytes_le=None, int=None):
        if bytes_le is not None:
            #0 8 16 24 32 40 48 56 64 72 80 88 96 104 112 120
            int = (ord(bytes_le[3]) << 120) + \
                    (ord(bytes_le[2]) << 112) + \
                    (ord(bytes_le[1]) << 104) + \
                    (ord(bytes_le[0]) << 96) + \
                    (ord(bytes_le[5]) << 88) + \
                    (ord(bytes_le[4]) << 80) + \
                    (ord(bytes_le[7]) << 72) + \
                    (ord(bytes_le[6]) << 64) + \
                    (ord(bytes_le[8]) << 56) + \
                    (ord(bytes_le[9]) << 48) + \
                    (ord(bytes_le[10]) << 40) + \
                    (ord(bytes_le[11]) << 32) + \
                    (ord(bytes_le[12]) << 24) + \
                    (ord(bytes_le[13]) << 16) + \
                    (ord(bytes_le[14]) << 8) + \
                    ord(bytes_le[15])
        self.__dict__['int'] = int
