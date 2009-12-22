#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from os import path

__port__ = 8898

class H(BaseHTTPRequestHandler):
    def do_GET(self):
		chunk = "chunks" + self.path
		if not path.exists(chunk):
			self.send_response(404)
			self.end_headers()
		else:
			self.send_response(200)
			self.end_headers()
			self.wfile.write(open(chunk).read())

if __name__ == "__main__":
    try:
        server = HTTPServer(('', __port__), H)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
