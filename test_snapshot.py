#!/usr/bin/env python
#-*- coding: utf-8 -*-


import unittest
from datetime import datetime
from snapshot import getFileSuffix, Snapshot

class SnapshotTest(unittest.TestCase):
    def test_getFileSuffix(self):
        dt = datetime(2009, 12, 27, 16, 38, 54, 136)
        self.assertEqual(getFileSuffix(dt), '2009-12-27-16-38-54-000136')

    def test_init(self):
        s = Snapshot('./', 'index.sqlite', './snapshots_t/')
        s.create()
        s.create()
        print "Latest %s" % s.replaceWithLatest()

if __name__ == '__main__':
    unittest.main()
