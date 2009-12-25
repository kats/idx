#!/usr/bin/env python
#-*- coding: utf-8 -*-

__CONNECTION_STRING__ = u'index.sqlite'

from sqlite3 import connect

connection = connect(__CONNECTION_STRING__)
cursor = connection.cursor()
cursor.execute('''drop table if exists state''')
cursor.execute('''drop index if exists pfrTransactions_index''')
cursor.execute('''drop table if exists pfrTransactions''')
cursor.execute('''vacuum''')

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

connection.commit()
connection.close()
