#-*- coding: utf-8 -*-

import config
import logging
from config import d_print

from os import remove
from os.path import isfile
from sqlite3 import connect, OperationalError

class PfrIndex:
    def __init__(self, filename):
        self.filename = filename
        self.log = logging.getLogger("pfridx")

    def create(self):
        try:
            if isfile(self.filename):
                d_print("File '%s' is already exist. Trying to remove..." % self.filename)
                remove(self.filename)
        except:
            self.log.error('create:fail')
            d_print("Cannot remove DB file '%s'. Please, close all connections to DB and try again." % self.filename)
            return False
        try:
            c = connect(self.filename)
            #c.execute('PRAGMA page_size=32768;')
            c.execute('create table state(offset integer)')
            # TODO(ibragim) remove id field
            c.execute('''
                create table pfrTransactions(
                    id integer primary key autoincrement,
                    orgId_hi integer, orgId_low integer, dcId_hi integer, dcId_low integer,
                    transactionTime integer, transactionType integer,
                    upfrCode text, accountingYear integer, providerIdHash integer, correctionType integer,
                    documents text, signatures text
                )''')
            c.execute('create index pfrTransactions_index on pfrTransactions(orgId_hi, orgId_low)')
            c.commit()
            c.close()
            self.log.info('create:ok')
            return True
        except OperationalError, e:
            log.error('create:fail:%s' % e)
            return False
        finally:
            if c: c.close()

    def validate(self):
        if not isfile(self.filename):
            return False
        try:
            c = connect(self.filename)
            res = c.execute('PRAGMA integrity_check').fetchone()
            if not res[0] == 'ok':
                c.close()
                return False

            res = c.execute('PRAGMA table_info(pfrTransactions)').fetchall()
            r = res and len(res) == 13 and \
                res[0][1] == 'id' and \
                res[1][1].lower() == 'orgid_hi' and \
                res[2][1].lower() == 'orgid_low' and \
                res[3][1].lower() == 'dcid_hi' and \
                res[4][1].lower() == 'dcid_low' and \
                res[5][1].lower() == 'transactiontime' and \
                res[6][1].lower() == 'transactiontype' and \
                res[7][1].lower() == 'upfrcode' and \
                res[8][1].lower() == 'accountingyear' and \
                res[9][1].lower() == 'provideridhash' and \
                res[10][1].lower() == 'correctiontype' and \
                res[11][1].lower() == 'documents' and \
                res[12][1].lower() == 'signatures'
            if not r:
                c.close()
                self.log.warning('validate:fail:pfrTransactions')
                return False

            res = c.execute('PRAGMA table_info(state)').fetchall()
            r = res and len(res) == 1 and \
                res[0][1] == 'offset'
            if not r:
                c.close()
                self.log.warning('validate:fail:state')
                return False

            res = c.execute('PRAGMA index_info(pfrTransactions_index)').fetchall()
            r = res and len(res) == 2 and \
                res[0][2].lower() == 'orgid_hi' and \
                res[1][2].lower() == 'orgid_low'
            if not r:
                c.close()
                self.log.warning('validate:fail:pfrTransactions_index')
                return False

            c.close()
            self.log.info('validate:ok')
            return True
        except OperationalError, e:
            log.error('validate:fail:%s' % e)
            return False
        finally:
            if c: c.close()

    def restore(self):
        return False
