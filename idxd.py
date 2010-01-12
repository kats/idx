#!/usr/bin/env python
#-*- coding: utf-8 -*-

import config
from time import sleep
from sqlite3 import connect, OperationalError
from struct import error

from os import remove
import os.path

from threading import *
import searchserver

stop_event = None

def __create_index():
    print "Trying to create DB in '%s'..." % config.IDX_FILENAME
    try:
        if os.path.isfile(config.IDX_FILENAME):
            print "File '%s' is already exist. Trying to remove..." % config.IDX_FILENAME
            remove(config.IDX_FILENAME)
    except:
        print "Cannot remove DB file '%s'. Please, close all connections to DB and try again." % config.IDX_FILENAME
        return False

    c = connect(config.IDX_FILENAME)
    #c.execute('PRAGMA page_size=32768;')
    c.execute('''
        create table state(offset integer)
        ''')
    c.execute('''
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
    c.execute('''
        create index pfrTransactions_index on pfrTransactions(orgId_hi, orgId_low)
        ''')
    c.commit()
    c.close()
    print "DB were created successfully."
    return True

def __validate_index():
    c = connect(config.IDX_FILENAME)
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
        return False

    res = c.execute('PRAGMA table_info(state)').fetchall()
    r = res and len(res) == 1 and \
        res[0][1] == 'offset'
    if not r:
        c.close()
        return False

    res = c.execute('PRAGMA index_info(pfrTransactions_index)').fetchall()
    r = res and len(res) == 2 and \
        res[0][2].lower() == 'orgid_hi' and \
        res[1][2].lower() == 'orgid_low'
    if not r:
        c.close()
        return False

    c.close()
    return True

def __restore_from_snapshot():
    return False

def __start_search_daemon(port, stop_event, end_long_run_update_event):
    t = Thread(target=searchserver.run, args=(port,stop_event, end_long_run_update_event))
    t.daemon = True
    t.start()
    return t

def status():
    c = connect(config.IDX_FILENAME)
    i = c.execute('select max(offset) from state').fetchone()[0] 
    print 'Current offset is %d' % (i if i <> None else 0)
    i = c.execute('select count(*) from pfrTransactions').fetchone()[0] 
    print 'Transactions in DB: %d' % (i if i <> None else 0)
    c.close()

def indexserver_run(kanso_filename, stop_event, end_long_run_update_event):
    from IndexServer import IndexServerUpdater
    from kstream import kstream
    from read_structs import read_structs
    import sys

    updater = IndexServerUpdater(config.IDX_FILENAME)
    ks = kstream(config.KANSO_FILENAME)

    print "Update server is started."
    offset = updater.offset
    while not stop_event.isSet():
        try:
            for b in ks.read(offset):
                for inner_offset, txn in read_structs(b):
                    updater.insert_record((offset + inner_offset, txn))
                    if stop_event.isSet(): break
                updater.commit()
        except error:
            pass
        except:
            print sys.exc_info()
            raise
        trials = 0
        while True:
            try:
                updater.commit()
                break
            except OperationalError as e:
                if trials > config.IDX_TRIALS:
                    raise e
                sleep(config.IDX_DB_BUSY_DELAY)

        if stop_event.isSet(): break
        offset = updater.offset
        #if offset == updater.offset: <-- too dangerous
        end_long_run_update_event.set()

        print "Data file processed up to %d offset" % updater.offset
        print "Sleep for %d seconds" % config.KANSO_READ_UPDATES_DELAY
        #status()
        sleep(config.KANSO_READ_UPDATES_DELAY)
    updater.commit()
    updater.stop()
    print "Update server is down."

def __start_update_daemon(kanso_filename, stop_event, end_long_run_update_event):
    t = Thread(target=indexserver_run, args=(kanso_filename,stop_event,end_long_run_update_event))
    t.daemon = True
    t.start()
    return t

import httplib
def __serve_forever(stop_event, t_search, t_update):
    try:
        while not stop_event.isSet():
            sleep(1)
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        c = httplib.HTTPConnection('127.0.0.1', config.IDX_WEBSERVER_PORT)
        c.request('STOP', '')
    t_search.join(10)
    t_update.join(10)

def run():
    print 'Start serving idxd...'
    print 'Verifying DB file...'
    if not os.path.isfile(config.IDX_FILENAME):
        print "File '%s' does not exist  " %  config.IDX_FILENAME
        __create_index()

    try:
        if not __validate_index():
            print 'Index DB is damaged. Trying to restore from latest snapshot.'
            if not __restore_from_snapshot():
                print 'Cannot retore from snapshot. Recreating index from scratch.'
                __create_index()
            else:
                print 'Index DB file were restored from snapshot.'
        else:
            print 'Index DB file is OK.'
    except OperationalError as e:
        print e
        print "Please, close all connections to DB and try again."
        return
    stop_event = Event()
    end_long_run_update_event = Event()
    t_search = __start_search_daemon(config.IDX_WEBSERVER_PORT, stop_event, end_long_run_update_event)
    t_update = __start_update_daemon(config.KANSO_FILENAME, stop_event, end_long_run_update_event)
    __serve_forever(stop_event, t_search, t_update)

if __name__ == '__main__':
    run()
