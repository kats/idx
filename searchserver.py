#!/usr/bin/env python
#-*- coding: utf-8 -*-

import config
from config import d_print
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from intUtils import splitInt128, combineInt128
from re import search
from sqlite3 import connect, OperationalError
from sys import exc_info
from time import sleep
from threading import Thread
from uuid import UUID

from logging import getLogger
log = getLogger('search')

class IndexSearcher:
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
        while True:
            try:
                resData = self.__get_results(query)
                break
            except OperationalError as e:
                d_print("Get result error")
                log.warning('search:%s' % e)
                trials += 1
                if trials >= config.IDX_TRIALS:
                    d_print("Has no more trials.")
                    log.error('search:fail')
                    raise e
                d_print("Will try again after delay...")
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

class SearchServer(HTTPServer):
    def __init__(self,server_address, RequestHandlerClass, events):
        self.events = events
        self.idx = IndexSearcher(config.IDX_FILENAME)
        HTTPServer.__init__(self, server_address, RequestHandlerClass)

class SearchRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.server.events and \
                    self.server.events.endupdate and \
                    not self.server.events.endupdate.isSet():
                self.send_error(503, "Waiting for long run update...")
                return
            id = search("orgId=([^&]*)", self.path)
            if not id:
                self.send_error(404, "Bad request: %s" % self.path)
                return
            id = UUID(id.group(1))

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Content-Encoding', 'utf-8')
            self.end_headers()

            for r in self.server.idx.search(id.int):
                self.wfile.write(r.encode('utf-8'))
        except:
            self.send_error(404, "Unexpected error: %s" % str(exc_info()[1]))
            raise

    def do_STOP(self):
        d_print('Shutting down search server...')
        log.info('stop')
        t = Thread(target=shutdown_server, args=(self.server,))
        t.daemon = True
        t.start()
    
    def shutdown(self):
        self.shutdown()
        self.idx.stop()

    def log_message(self, format, *args):
        log.info('%s\t%s' % (format%args, self.address_string()))

    def log_request(self, code='-', size='-'):
        self.log_message('request:"%s"\t%d', self.requestline, code)

    def log_error(self, format, *args):
        self.log_message('error:%d\t"%s"' % args)

def shutdown_server(server):
    server.shutdown()
    if server.events and server.events.stop:
        server.events.stop.set()
    d_print('Search server is down.')
    log.info('shutdown')

def run(port, events=None):
    s = SearchServer(('', port), SearchRequestHandler, events)
    d_print('Search server started')
    log.info('run')
    s.serve_forever()

def main():
    try:
        s = SearchServer(('', config.IDX_WEBSERVER_PORT), SearchRequestHandler)
        print 'Search server started.'
        s.serve_forever()
    except KeyboardInterrupt:
        s.socket.close()
        print 'Search server is down.'

if __name__ == '__main__':
    main()
