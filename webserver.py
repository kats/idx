#!/usr/bin/env python
#-*- coding: utf-8 -*-

__PORT__ = 8092

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import sys
import re
import uuid

from IndexServer import IndexServer

if __name__ == '__main__':
    IdxServer = IndexServer()

class IndexSearchRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            id = re.search("orgId=([^&]*)", self.path)
            id = id.group(1)
            # big-endian string expected
            id = uuid.UUID(id)

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            for sr in IdxServer.search(id.int):
                self.wfile.write(sr)
                self.wfile.write('\n')
        except:
            # Error ether in parsing or param.
            self.send_error(404, "Unexpected error: %s" % sys.exc_info()[0])
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

