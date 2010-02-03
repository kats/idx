#!/usr/bin/env python
#-*- coding: utf-8 -*-

import config
import logging

from index import PfrIndex
from snapshot import Snapshot
import searchserver
import indexserver

from collections import namedtuple
from httplib import HTTPConnection
from sys import exc_info
from threading import Thread, Event
from time import sleep

log = logging.getLogger('idxd')

def __start_search_daemon(port, events):
    t = Thread(target=searchserver.run, args=(port,events))
    t.daemon = True
    t.start()
    return t

def __start_update_daemon(kanso_filenames, events):
    t = Thread(target=indexserver.run, args=(kanso_filenames,events))
    t.daemon = True
    t.start()
    return t

def __serve_forever(t_search, t_update, events):
    # TODO: process kill signal and alternatives
    try:
        while not events.stop.isSet():
            sleep(1)
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        c = HTTPConnection('127.0.0.1', config.IDX_WEBSERVER_PORT)
        c.request('STOP', '')
    t_search.join(10)
    t_update.join(10)
    log.info('finish')

def run():
    log.info('start')
    print 'Start serving idxd...'
    idx = PfrIndex(config.IDX_FILENAME)
    snapshot_manager = Snapshot()
    if not idx.validate() and \
            not snapshot_manager.restore(PfrIndex) and \
            not idx.create():
        print "Please, close all connections to DB and try again."
        return -1

    Events = namedtuple("Events", "stop endupdate")
    events = Events(Event(), Event())
    __serve_forever( \
            __start_search_daemon(config.IDX_WEBSERVER_PORT, events), \
            __start_update_daemon((config.KANSO_FILENAME, config.KANSO_FILENAME2), events), \
            events)

if __name__ == '__main__':
    try:
        run()
    except:
        log.critical('unexpected:%s' % str(exc_info()[1]))
        raise
