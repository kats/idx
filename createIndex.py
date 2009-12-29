#!/usr/bin/env python
#-*- coding: utf-8 -*-

__CONNECTION_STRING = u'index.sqlite'

from os import remove
import os.path

if os.path.isfile(__CONNECTION_STRING):
    remove(__CONNECTION_STRING)

from sqlite3 import connect

connection = connect(__CONNECTION_STRING)
cursor = connection.cursor()
#cursor.execute('PRAGMA page_size=32768;')

cursor.execute('''
        create table state(offset integer)
        ''')
cursor.execute('''
        create table pfrTransactions(
            id integer primary key autoincrement,
            orgId_hi integer,
            orgid_low integer,
            dcId_hi integer,
            dcId_low integer,
            transactionTime integer,
            transactionType integer,
            upfrCode text,
            accountingYear integer,
            providerIdHash integer,
            correctionType integer,
            documents text,
            signatures text
        )
        ''')

cursor.execute('''
        create index pfrTransactions_index on pfrTransactions(orgId_hi, orgId_low)
        ''')

connection.commit()
connection.close()
