#!/usr/bin/env python
#-*- coding: utf-8 -*-


import guid
import uuid
from datetime import datetime
from struct import unpack_from

def testPerformance():
    start = datetime.now()
    for i in xrange(1, 250000):
        uuid.UUID(bytes_le = str('1234567890123456'))
    stop = datetime.now()
    delta = str(stop - start)
    print "UUID(bytes_le) time: " + delta

    start = datetime.now()
    for i in xrange(1, 250000):
        guid.UUID(bytes_le = str('1234567890123456'))
    stop = datetime.now()
    delta = str(stop - start)
    print "GUID(bytes_le) time: " + delta

    start = datetime.now()
    for i in xrange(1, 250000):
        guid.UUID(int=0)
    stop = datetime.now()
    delta = str(stop - start)
    print "UUID time (int): " + delta

    start = datetime.now()
    for i in xrange(1, 250000):
        ints = unpack_from("=QQ", '1234567890123456')
    stop = datetime.now()
    delta = str(stop - start)
    print "Unpack bytes_le with '=QQ': " + delta


if __name__ == '__main__':
    testPerformance()
