#!/usr/bin/env python
#-*- coding: utf-8 -*-

from sqlite3 import connect
from uuid import UUID
from intUtils import *

class IndexServer:
    def __init__(self, connectionString):
        self.connection = connect(connectionString)
    def search(self, query):
        cursor = self.connection.cursor()
        cursor.execute('''
            select orgId_hi, orgId_low, dcId_hi, dcId_low,
                transactionTime, transactionType, upfrCode, 
                accountingYear, providerIdHash, correctionType, 
                documents, signatures
            from pfrTransactions
            where (orgId_hi = %d) and (orgId_low = %d)
            order by dcId_hi, dcId_low, transactionTime''' % splitInt128(query))
        resData = cursor.fetchall()
        cursor.close()
        res = ""
        a = 1
        for row in resData:
            #print row
            r = '%s\t%s\t%d\t%d\t"%s"\t%d\t%d\t%d\t\n\n%s\n%s\n\n' % \
                ((UUID(int=combineInt128(row[0], row[1])), UUID(int=combineInt128(row[2], row[3]))) + row[4:])
            if a == 1:
                print r
                a = 0
            res += r
        return res

class IndexServerUpdater:
    def __init__(self, connectionString):
        self.connection = connect(connectionString)
        self.pcounter = 0
    def __format_signatures(self, signatures):
        res = ""
        for s in signatures:
            res += '%s\t%s\t%d\t%d\t%d\n' % (s.id, s.docId, s.type, s.kansoOffset, s.contentLen)
        return res
    def __format_documents(self, documents):
        res = ""
        for d in documents:
            res += '%s\t%d\t%d\t"%s"\t%d\t%d\n' % (d.id, d.type, d.formKey, d.fileName.decode('utf-8'), d.kansoOffset, d.contentLen)
        return res
    def insert_record(self, rec):
        r = rec[0]
        cursor = self.connection.cursor()
        cursor.execute('''
           insert into pfrTransactions(
           orgId_hi, orgId_low,
            dcId_hi, dcId_low,
            transactionTime,
            transactionType,
            upfrCode,
            accountingYear,
            providerIdHash,
            correctionType,
            documents,
            signatures) values(?,?,?,?,?,?,?,?,?,?,?,?)''',
            splitInt128(r.orgId.int) + splitInt128(r.dcId.int) +
            (toSignedInt64(r.time),
                r.type,
                r.upfrCode,
                r.accYear,
                r.provId,
                r.corrType,
                self.__format_documents(rec[1]),
                self.__format_signatures(rec[2]))
        )
        cursor.close()
        self.pcounter += 1
        if self.pcounter == 500:
            self.pcounter = 0
            self.connection.commit()
    def commit(self):
        self.connection.commit()
