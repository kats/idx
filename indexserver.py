#!/usr/bin/env python
#-*- coding: utf-8 -*-

import config
from config import d_print
from intUtils import splitInt128, toSignedInt64

from datetime import datetime
from socket import error as s_error
from sqlite3 import connect, OperationalError
from struct import error
from sys import exc_info
from time import sleep
from uuid import UUID

from kstream import kstream
from read_structs import read_structs
from snapshot import Snapshot

from logging import getLogger
log = getLogger('index')

def trydb(fn, fromat, *args):
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

# TODO: Add loging
class IndexServerUpdater:
    def __init__(self, connectionString):
        self.__connectionString = connectionString
        self.start()

    def __purge_state_table(self):
        self.connection.execute('delete from state where offset not in (select max(offset) from state)')

    def __get_max_offset(self):
        o = self.connection.execute('select max(offset) from state').fetchone()[0]
        return o if o <> None else 0

    def __insert_new_offset(self):
        self.connection.execute('insert into state(offset) values(?)', (self.offset,))

    def start(self):
        self.connection = connect(self.__connectionString)
        self.connection.isolation_level = 'DEFERRED'
        self.connection.execute('PRAGMA synchronous=OFF')
        self.begin()
        self.__purge_state_table()
        self.__purge_state_table2()
        self.connection.commit()
        self.offset = self.__get_max_offset()
        self.offset2 = self.__get_max_offset2()
        self.pcounter = 0

    def __get_max_offset2(self):
        o = self.connection.execute('select max(offset) from state2').fetchone()[0]
        return o if o <> None else 0

    def __insert_new_offset2(self):
        self.connection.execute('insert into state2(offset) values(?)', (self.offset2,))

    def __purge_state_table2(self):
        self.connection.execute('delete from state2 where offset not in (select max(offset) from state2)')

    def __format_documents(self, documents):
        res = ""
        for d in documents:
            res += '%s\t%d\t%d\t%d\t"%s"\t%d\t%d\n' % \
                (d.id, d.type, d.formKey, d.documentFlags, d.fileName.decode('cp1251'), d.kansoOffset, d.contentLen)
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

def run(kanso_filenames, events):
    d_print("Update server is started.")
    log.info('start')

    # DANGEROUS: Could crash updater
    updater = IndexServerUpdater(config.IDX_FILENAME)

    ks = kstream(config.KANSO_FILENAME)
    ks2 = kstream(config.KANSO_FILENAME2)    
    offset = updater.offset
    offset2 = updater.offset2
    snapshot_manager = Snapshot('.', config.IDX_FILENAME, config.IDX_SNAPSHOT_DIR)
    while not events.stop.isSet():
        start = datetime.now()
        events.endupdate.clear()
        try:
            # Important note:
            # ---------------
            #    We guess that records (transactions in our case) stored in KANSO does not cross 
            # KANSO chunk border and it is because of KANSO atomic writes.
            for b in ks.read(offset):
                trydb(updater.begin, 'db-begin:%s')
                try:
                    for inner_offset, txn in read_structs(b):
                        trydb(updater.insert_record, 'db-insert:%s', (offset + inner_offset, txn))
                        if events.stop.isSet(): break
                except error, e:
                    log.warning('read_structs:%s' % e)
                trydb(updater.commit, 'db-commit:%s')
                offset = updater.offset
            for b in ks2.read(offset2):
                trydb(updater.begin, 'db-begin:%s')
                try:
                    for inner_offset, txn in read_structs(b):
                        trydb(updater.insert_record2, 'db-insert:%s', (offset2 + inner_offset, txn))
                        if events.stop.isSet(): break
                except error, e:
                    log.warning('read_structs:%s' % e)
                trydb(updater.commit, 'db-commit:%s') 
                offset2 = updater.offset2
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

        # The fact is snapshot_manager changes index on start and stop (purges and commit),
        # So, because of this fact we have to create snapshot during update phase and it is 
        # an issue: we have to do not start search until snapshot completes.
        if snapshot_manager.isTime():
            start = datetime.now()
            try:
                trydb(updater.stop, 'updater:stop:error:%s')
            except error, e:
                continue
            try:
                snapshot_manager.create()
                log.info('snapshot:ok:%s' % str(datetime.now() - start))
            except:
                log.error('snapshot:error:%s' % str(exc_info()[1]))
            finally:
                # DANGEROUS: Could crash updater
                trydb(updater.start, 'updater:start:error:%s')       
        
        events.endupdate.set()
        log.info('update:completed:%s' % str(datetime.now() - start))
        d_print("update:Sleep for %d seconds" % config.KANSO_READ_UPDATES_DELAY)
        log.info('update:offset:%s' % updater.offset)
        log.info('update:offset2:%s' % updater.offset2)

        if events.stop.wait(config.KANSO_READ_UPDATES_DELAY):
            break

    updater.stop()
    d_print("Update server is down.")
    log.info('shutdown')
