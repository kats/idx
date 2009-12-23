#!/usr/bin/env python
#-*- coding: utf-8 -*-

__CONNECTION_STRING__ = u'index.sqlite'
from sqlite3 import connect

class IndexServer:
    def __init__(self):
        self.connection = connect(__CONNECTION_STRING__)

    def search(self, query):
        cursor = self.connection.cursor()
        id_hi = query >> 64
        id_low = query & 0xFFFFFFFFFFFFFFFF
        cursor.execute('select * from pfrTransactions where (orgId_hi = %d) and (orgId_low = %d) order by dcId_hi, dcId_low, transactionTime' % (id_hi, id_low))
        res = cursor.fetchall()
        cursor.close()

        return res
