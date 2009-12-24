#!/usr/bin/env python
#-*- coding: utf-8 -*-

__PORT__ = 8092

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import sys
import re
import uuid

from IndexServer import IndexServer

if __name__ == '__main__':
    IdxServer = IndexServer("index.sqlite")

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

            self.wfile.write(IdxServer.search(id.int).encode('utf-8'))
        except:
            # Error ether in parsing or param.
            self.send_error(404, "Unexpected error: %s\n%s\n%s" % sys.exc_info())
            raise

def main():
    try:
        server = HTTPServer(('', __PORT__), IndexSearchRequestHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

