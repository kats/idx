#!/usr/bin/env python
#-*- coding: utf-8 -*-

from read_structs import read_structs
from struct import error

OUT = 'guids.txt'
FNAME1 = 'test_data/transactions'
FNAME2 = 'test_data/outgoingTransactions'
IGNORE = '11111111-1111-1111-1111-111111111111'

def __get(filenames):
    for n in filenames:
        with open(n, 'rb') as f:
            try:
                for o, txn in read_structs(f.read()):
                    print txn[0]
                    yield txn[0].orgId
            except error:
                pass

if __name__ == '__main__':
    with open(OUT, 'w') as f:
        for g in __get((FNAME2,)):
            s = str(g)
            if s != IGNORE:
                f.write(str(g) + '\n')
            print g
