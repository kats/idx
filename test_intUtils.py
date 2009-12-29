#!/usr/bin/env python
#-*- coding: utf-8 -*-


import unittest
from uuid import UUID as uuid_UUID
from guid import UUID
from struct import unpack_from
from intUtils import uuid2searchInts 

sample_UUID = '1234567890123456'

class TestUUID2SearchInts(unittest.TestCase):
    def testConversion(self):
        u = uuid_UUID(bytes_le = sample_UUID)
        ints = unpack_from('=QQ', sample_UUID)
        ints2 = uuid2searchInts(u) 
        self.assertEqual(ints, ints2)

if __name__ == '__main__':
    unittest.main()
