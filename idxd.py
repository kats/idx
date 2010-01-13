#!/usr/bin/env python
#-*- coding: utf-8 -*-

import config

from index import PfrIndex
import searchserver
import IndexServer as indexserver

from collections import namedtuple
from httplib import HTTPConnection
from os.path import isfile
from threading import Thread, Event
from time import sleep

def __start_search_daemon(port, events):
    t = Thread(target=searchserver.run, args=(port,events))
    t.daemon = True
    t.start()
    return t

def __start_update_daemon(kanso_filename, events):
    t = Thread(target=indexserver.run, args=(kanso_filename, events))
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

def run():
    print 'Start serving idxd...'
    idx = PfrIndex(config.IDX_FILENAME)
    if not isfile(config.IDX_FILENAME):
        idx.create()
    if not idx.validate() and not idx.restore() and not idx.create():
        print "Please, close all connections to DB and try again."
        return -1

    Events = namedtuple("Events", "stop endupdate")
    events = Events(Event(), Event())
    __serve_forever( \
            __start_search_daemon(config.IDX_WEBSERVER_PORT, events), \
            __start_update_daemon(config.KANSO_FILENAME, events), \
            events)

if __name__ == '__main__':
    run()
