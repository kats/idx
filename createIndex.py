#!/usr/bin/env python
#-*- coding: utf-8 -*-

__CONNECTION_STRING = u'index.sqlite'

from index import PfrIndex
from os import remove
from os.path import isfile

if __name__ == '__main__':  
    if isfile(__CONNECTION_STRING):
        remove(__CONNECTION_STRING)
    idx = PrfIndex(__CONNECTION_STRING)
