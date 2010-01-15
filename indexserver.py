#!/usr/bin/env python
#-*- coding: utf-8 -*-

import config
from config import d_print
from intUtils import splitInt128, toSignedInt64
from socket import error as s_error
from sqlite3 import connect, OperationalError
from struct import error
from sys import exc_info
from time import sleep
from uuid import UUID

from kstream import kstream
from read_structs import read_structs

from logging import getLogger
log = getLogger('index')

# TODO: Add loging
class IndexServerUpdater:
    def __init__(self, connectionString):
        self.__connectionString = connectionString
        self.connection = connect(connectionString)
        self.connection.isolation_level = 'DEFERRED'
        self.connection.execute('PRAGMA synchronous=OFF')
        self.begin()
        self.__purge_state_table()
        self.__purge_state_table2()
        self.connection.commit()
        self.offset = self.__get_max_offset()
        self.offset2 = self.__get_max_offset2()
        self.pcounter = 0

    def __get_max_offset(self):
        o = self.connection.execute('select max(offset) from state').fetchone()[0]
        return o if o <> None else 0

    def __insert_new_offset(self):
        self.connection.execute('insert into state(offset) values(?)', (self.offset,))

    def __purge_state_table(self):
        self.connection.execute('delete from state where offset not in (select max(offset) from state)')

    def __get_max_offset2(self):
        o = self.connection.execute('select max(offset) from state2').fetchone()[0]
        return o if o <> None else 0

    def __insert_new_offset2(self):
        self.connection.execute('insert into state2(offset) values(?)', (self.offset,))

    def __purge_state_table2(self):
        self.connection.execute('delete from state2 where offset not in (select max(offset) from state2)')

    def __format_documents(self, documents):
        res = ""
        for d in documents:
            res += '%s\t%d\t%d\t"%s"\t%d\t%d\n' % \
                (d.id, d.type, d.formKey, d.fileName.decode('utf-8'), d.kansoOffset, d.contentLen)
        return res

    def __format_signatures(self, signatures):
        res = ""
        for s in signatures:
            res += '%s\t%s\t%d\t%d\t%d\n' % (s.id, s.docId, s.type, s.kansoOffset, s.contentLen)
        return res

    def insert_record(self, rec):
        o, tnx = rec
        r, docs, signs = tnx
        self.connection.execute('''
           insert into pfrTransactions(
            orgId_hi, orgId_low, dcId_hi, dcId_low,
            transactionTime, transactionType,
            upfrCode, accountingYear, providerIdHash, correctionType,
            documents, signatures) values(?,?,?,?,?,?,?,?,?,?,?,?)''',
            splitInt128(r.orgId.int) + splitInt128(r.dcId.int) +
            (toSignedInt64(r.time), r.type,
                r.upfrCode, r.accYear, r.provId, r.corrType,
                self.__format_documents(docs), self.__format_signatures(signs))
        )
        self.offset = o
        self.pcounter += 1
        if self.pcounter == config.IDX_ITEMS_PER_COMMIT:
            self.pcounter = 0
            self.commit()
            self.begin()

    def insert_record2(self, rec):
        o, tnx = rec
        r, docs, signs = tnx
        self.connection.execute('''
           insert into pfrTransactions(
            orgId_hi, orgId_low, dcId_hi, dcId_low,
            transactionTime, transactionType,
            upfrCode, accountingYear, providerIdHash, correctionType,
            documents, signatures) values(?,?,?,?,?,?,?,?,?,?,?,?)''',
            splitInt128(r.orgId.int) + splitInt128(r.dcId.int) +
            (toSignedInt64(r.time), r.type,
                r.upfrCode, r.accYear, r.provId, r.corrType,
                self.__format_documents(docs), self.__format_signatures(signs))
        )
        self.offset2 = o
        self.pcounter += 1
        if self.pcounter == config.IDX_ITEMS_PER_COMMIT:
            self.pcounter = 0
            self.commit()
            self.begin()

    def begin(self):
        self.connection.execute('BEGIN DEFERRED TRANSACTION')

    def commit(self):
        self.__insert_new_offset()
        self.__insert_new_offset2()
        self.connection.commit()

    def stop(self):
        self.commit()
        self.connection.close()

def __try(fn, fromat, *args):
    trials = 0
    while True:
        try:
            fn(*args)
            break
        except OperationalError as e:
            log.warning(format % str(e))
            trials += 1
            if trials > config.IDX_TRIALS:
                raise e
            sleep(config.IDX_DB_BUSY_DELAY)

def run(kanso_filenames, events):
    d_print("Update server is started.")
    log.info('start')

    updater = IndexServerUpdater(config.IDX_FILENAME)

    ks = kstream(config.KANSO_FILENAME)
    ks2 = kstream(config.KANSO_FILENAME2)    
    offset = updater.offset
    offset2 = updater.offset2
    while not events.stop.isSet():
        events.endupdate.clear()
        try:
            # TODO(kats): Resolve "transaction that cross two chanks border" problem
            for b in ks.read(offset):
                __try(updater.begin, 'db-begin:%s')
                try:
                    for inner_offset, txn in read_structs(b):
                        __try(updater.insert_record, 'db-insert:%s', (offset + inner_offset, txn))
                        if events.stop.isSet(): break
                except error, e:
                    log.warning('read_structs:%s' % e)
                __try(updater.commit, 'db-commit:%s')
            for b in ks2.read(offset2):
                __try(updater.begin, 'db-begin:%s')
                try:
                    for inner_offset, txn in read_structs(b):
                        __try(updater.insert_record2, 'db-insert:%s', (offset2 + inner_offset, txn))
                        if events.stop.isSet(): break
                except error, e:
                    log.warning('read_structs:%s' % e)
                __try(updater.commit, 'db-commit:%s') 
        except s_error, e:
            log.warning('nokanso:%s' % e)
        except:
            # TODO:log indexserver shutdown unexpectedly (email?)
            d_print(exc_info())
            log.critical('unexpected:%s' % str(exc_info()[1]))
            events.endupdate.set()
            updater.stop()
            raise
        if events.stop.isSet(): break
        offset = updater.offset
        offset2 = updater.offset2
        events.endupdate.set()
        d_print("Data file processed up to %d offset" % updater.offset)
        d_print("Sleep for %d seconds" % config.KANSO_READ_UPDATES_DELAY)
        log.info('update:offset:%s' % updater.offset)
        if events.stop.wait(config.KANSO_READ_UPDATES_DELAY):
            break

    updater.stop()
    d_print("Update server is down.")
    log.info('shutdown')
