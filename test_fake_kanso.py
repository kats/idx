#!/usr/bin/env python
#-*- coding: utf-8 -*-

import fake_kanso
from kstream import *
from IndexServer import *
from read_structs import read_structs


if __name__ == '__main__':

    fake_kanso.run()

    import datetime
    start = datetime.datetime.now()

    updater = IndexServerUpdater("index.sqlite")

    offset = 0
    ks = kstream("kanso://127.0.0.1/pfr/test/transactions")
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
