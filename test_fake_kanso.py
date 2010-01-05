#!/usr/bin/env python
#-*- coding: utf-8 -*-

import fake_kanso
from kstream import *
from IndexServer import *
from read_structs import read_structs

import datetime
start = datetime.datetime.now()

updater = IndexServerUpdater("index.sqlite")
fake_kanso.run()
offset = 0
ks = kstream("kanso://localhost/pfr/test/transactions")
while fake_kanso.append():
    inner_offset = 0
    try:
        for txn in read_structs(ks.read(offset)):
            updater.insert_record(txn)
            inner_offset =  txn[0]
    except: pass
    offset += inner_offset
    inner_offset = 0
updater.commit()

print str(datetime.datetime.now() - start)
