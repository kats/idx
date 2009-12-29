#!/usr/bin/env python
#-*- coding: utf-8 -*-

__INT64MASK     = 0xFFFFFFFFFFFFFFFFL
__INT64MAX      = 0x7FFFFFFFFFFFFFFFL

def toSignedInt64(longInt):
    if longInt > __INT64MAX:
        return int((longInt & __INT64MAX ) - __INT64MAX - 1)
    else: return longInt

def toUnsignedInt64(int64):
    if int64 < 0:
        return __INT64MASK + int64 + 1
    else: return int64

def splitInt128(int128):
    return toSignedInt64(int128 >> 64), toSignedInt64(int128 & __INT64MASK)

def combineInt128(int64_hi, int64_low):
    return (toUnsignedInt64(int64_hi) << 64) + toUnsignedInt64(int64_low)

from struct import unpack_from
def uuid2searchInts(uuid):
    return unpack_from('=QQ', uuid.bytes_le)
