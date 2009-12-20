#!/usr/bin/env python
#-*- coding: utf-8 -*-

__PORT__ = 8092

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from IndexServer import IndexServer

if __name__ == '__main__':
    IdxServer = IndexServer()

class IndexSearchRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            for sr in IdxServer.search(self.path):
                self.wfile.write(sr)
            return
                
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)    

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

