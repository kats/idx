#!/usr/bin/env python
#-*- coding: utf-8 -*-

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import sys
import re
import uuid

from IndexServer import IndexServer
from threading import Thread
import config

class SearchServer(HTTPServer):
    def __init__(self,server_address, RequestHandlerClass, stop_event):
        self.stop_event = stop_event
        self.idx_server = IndexServer(config.IDX_FILENAME_STRINING)
        HTTPServer.__init__(self, server_address, RequestHandlerClass)

class IndexSearchRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            id = re.search("orgId=([^&]*)", self.path)
            if not id:
                self.send_error(404, "Bad request: %s" % self.path)
                return
            id = uuid.UUID(id.group(1))

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Content-Encoding', 'utf-8')
            self.end_headers()

            for r in self.server.idx_server.search(id.int):
                self.wfile.write(r.encode('utf-8'))
        except:
            self.send_error(404, "Unexpected error: %s\n%s\n%s" % sys.exc_info())
            raise

    def do_STOP(self):
        print 'Shutting down search server...'
        t = Thread(target=shutdown_server, args=(self.server,))
        t.daemon = True
        t.start()
    
    def shutdown(self):
        self.shutdown()
        self.idx_server.stop()

def shutdown_server(server):
    server.shutdown()
    server.stop_event.set()
    print 'Search server is down.'

def run(port, stop_event=None):
    s = SearchServer(('', port), IndexSearchRequestHandler, stop_event)
    print 'Search server started'
    s.serve_forever()

def main():
    try:
        s = SearchServer(('', config.IDX_WEBSERVER_PORT), IndexSearchRequestHandler)
        print 'Search server started.'
        s.serve_forever()
    except KeyboardInterrupt:
        s.socket.close()
        print 'Search server is down.'

if __name__ == '__main__':
    main()
