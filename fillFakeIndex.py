#!/usr/bin/env python
#-*- coding: utf-8 -*-

__CONNECTION_STRING__ = u'index.sqlite'

from sqlite3 import connect, Error
from random import randint

connection = connect(__CONNECTION_STRING__)
cursor = connection.cursor()

cursor.execute('''delete from state''')
cursor.execute('''delete from pfrSignatures''')
cursor.execute('''delete from pfrDocuments''')
cursor.execute('''delete from pfrTransactions''')

for i in xrange(1,100):
    cursor.execute('''
       insert into pfrTransactions(
           orgId_hi, orgId_low, 
            dcId_hi, dcId_low, 
            transactionTime, 
            transactionType, 
            upfrCode, 
            accountingYear, 
            providerIdHash,
            correctionType) values(?,?,?,?,?,?,?,?,?,?)''', 
            (randint(0,10000000000), randint(0,10000000000),
                randint(0,10000000000), randint(0,10000000000),
                randint(0,10000000000),
                randint(0,10000000000),
                u'upfrCode%d' % randint(0,10000000000),
                randint(0,10000000000),
                randint(0,10000000000),
                randint(0,10000000000),))

cursor.execute("select last_insert_rowid() from pfrTransactions")
tr_id = cursor.fetchone()[0]
cursor.close()

print tr_id
connection.commit()
connection.close()
