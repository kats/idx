#!/usr/bin/env python
#-*- coding: utf-8 -*-

from uuid import UUID as uuid_UUID
from struct import unpack_from

class UUID(uuid_UUID):
    def __init__(self, bytes_le=None, int=None):
        if bytes_le is not None:
            bytes_le = (bytes_le[6] + bytes_le[7] + bytes_le[4] + bytes_le[5] +
                     bytes_le[0] + bytes_le[1] + bytes_le[2] + bytes_le[3] +
                     bytes_le[15] + bytes_le[14] + bytes_le[13] + bytes_le[12] +
                     bytes_le[11] + bytes_le[10] + bytes_le[9] + bytes_le[8])
            
            ints = unpack_from("=QQ", bytes_le)
            int = (ints[0] << 64) + ints[1]
        self.__dict__['int'] = int
