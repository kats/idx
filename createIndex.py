#!/usr/bin/env python
#-*- coding: utf-8 -*-

__CONNECTION_STRING__ = u'index.sqlite'

from sqlite3 import connect

connection = connect(__CONNECTION_STRING__)
cursor = connection.cursor()
cursor.execute('''drop table if exists state''')
cursor.execute('''drop table if exists pfrSignatures''')
cursor.execute('''drop table if exists pfrDocuments''')
cursor.execute('''drop index if exists pfrTransactions_index''')
cursor.execute('''drop table if exists pfrTransactions''')
cursor.execute('''vacuum''')

cursor.execute('''
        create table state(offeset integer)
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
            correctionType integer
        )
        ''')
cursor.execute('''
        create index pfrTransactions_index on pfrTransactions(orgId_hi, orgId_low)
        ''')
cursor.execute('''
        create table pfrDocuments(
            tr_id integer references pfrTransactions(id),
            id_hi integer,
            id_low integer,
            type integer,
            formKey integer,
            fileName text,
            kansoOffset integer,
            contentLen integer
        )
        ''')
cursor.execute('''
        create table pfrSignatures(
            tr_id integer references pfrTransactions(id),
            id_hi integer,
            id_low integer,
            docId_hi integer,
            docId_low integer,
            contentLen integer,
            kansoOffset integer
        )
        ''')

connection.commit()
connection.close()
