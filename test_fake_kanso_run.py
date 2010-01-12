#!/usr/bin/env python
#-*- coding: utf-8 -*-

from sqlite3 import connect
from time import sleep

import fake_kanso
import config

SLEEP = 2

if __name__ == '__main__':
    fake_kanso.run()

    i = 0
    while 1:
        fake_kanso.append()
        i += 1
        print "Append #%d, sleep for %d secs" % (i, SLEEP)
        sleep(SLEEP)
