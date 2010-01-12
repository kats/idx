#!/usr/bin/env python
#-*- coding: utf-8 -*-

from sqlite3 import connect, OperationalError
from uuid import UUID
from intUtils import *
import config
from time import sleep

class IndexServer:
    def __init__(self, connectionString):
        self.__connectionString = connectionString
        self.start()

    def __get_results(self, query):
        cursor = self.connection.cursor()
        cursor.execute('''
            select orgId_hi, orgId_low, dcId_hi, dcId_low,
                transactionTime, transactionType, upfrCode, 
                accountingYear, providerIdHash, correctionType, 
                documents, signatures
            from pfrTransactions
                where (orgId_hi = %d) and (orgId_low = %d)
                order by dcId_hi, dcId_low, transactionTime''' % splitInt128(query))
        res = cursor.fetchall()
        cursor.close()
        return res

    def search(self, query):
        trials = 0
        hasNoResult = False
        while True:
            try:
                resData = self.__get_results(query)
                break
            except OperationalError as e:
                print "Get result error"
                trials += 1
                if trials >= config.IDX_TRIALS:
                    "Has no more trials."
                    raise e
                print "Will try again after delay..."
                sleep(config.IDX_DB_BUSY_DELAY)

        for row in resData:
            r = '%s\t%s\t%d\t%d\t"%s"\t%d\t%d\t%d\t\n\n%s\n%s\n\n' % \
            ((UUID(int=combineInt128(row[0], row[1])), UUID(int=combineInt128(row[2], row[3]))) + row[4:])
            yield r

    def start(self):
        self.connection = connect(self.__connectionString)
        self.connection.isolation_level = 'DEFERRED'

    def stop(self):
        self.connection.close()

# TODO: Add loging
class IndexServerUpdater:
    def __init__(self, connectionString):
        self.__connectionString = connectionString
        self.connection = connect(connectionString)
        self.connection.isolation_level = 'DEFERRED'
        self.connection.execute('PRAGMA synchronous=OFF')
        self.begin()
        self.__purge_state_table()
        self.pcounter = 0
        self.offset = self.__get_max_offset()
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
    def __get_max_offset(self):
        o = self.connection.execute('select max(offset) from state').fetchone()[0]
        return o if o <> None else 0
    def __insert_new_offset(self):
        self.connection.execute('insert into state(offset) values(?)', (self.offset,))
    def __purge_state_table(self):
        self.connection.execute('delete from state where offset not in (select max(offset) from state)').fetchall()
    def insert_record(self, rec):
        o, tnx = rec
        r, docs, signs = tnx
        self.connection.execute('''
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
                self.__format_documents(docs),
                self.__format_signatures(signs))
        )
        self.offset = o
        self.pcounter += 1
        if self.pcounter == config.IDX_ITEMS_PER_COMMIT:
            self.pcounter = 0
            self.commit()
            self.begin()

    def begin(self):
        self.connection.execute('BEGIN DEFERRED TRANSACTION')
        pass

    def commit(self):
        self.__insert_new_offset()
        self.connection.commit()

    def stop(self):
        self.commit()
        self.connection.close()
