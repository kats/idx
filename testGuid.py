#!/usr/bin/env python
#-*- coding: utf-8 -*-


import unittest
import guid
import uuid

class UUIDTests(unittest.TestCase):
    def testEqual(self):
        g = guid.UUID(bytes_le = str('1234567890123456'))
        u = uuid.UUID(bytes_le = str('1234567890123456'))

        self.assertEqual(g.int, u.int)
        self.assertEqual(g.hex, u.hex)

from datetime import datetime
def testPerformance():
    start = datetime.now()
    for i in xrange(1, 250000):
        uuid.UUID(bytes_le = str('1234567890123456'))
    stop = datetime.now()
    delta = str(stop - start)
    print "UUID time: " + delta

    start = datetime.now()
    for i in xrange(1, 250000):
        guid.UUID(bytes_le = str('1234567890123456'))
    stop = datetime.now()
    delta = str(stop - start)
    print "GUID time: " + delta

    start = datetime.now()
    for i in xrange(1, 250000):
        guid.UUID(int=0)
    stop = datetime.now()
    delta = str(stop - start)
    print "UUID time (int): " + delta

if __name__ == '__main__':
    unittest.main()
