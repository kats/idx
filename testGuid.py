#!/usr/bin/env python
#-*- coding: utf-8 -*-


import unittest
import guid
import uuid

class UUIDTests(unittest.TestCase):
    def testEqual(self):
        g = guid.UUID(bytes_le = str('1234567890123456'))
        u = uuid.UUID(bytes_le = str('1234567890123456'))
        print '%s' % g.hex
        print '%s' % u.hex

        self.assertEqual(g.int, u.int)
        self.assertEqual(g.hex, u.hex)

if __name__ == '__main__':
    unittest.main()
