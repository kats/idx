#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

__port__ = 22222

class H(BaseHTTPRequestHandler):
    def do_GET(self):
		self.send_response(200)
		self.end_headers()
		self.wfile.write("4c44ed6d-4b46-4093-93f1-6b29a95e08ea;127.0.0.1:8897,8898,8896\n")

if __name__ == "__main__":
    try:
        server = HTTPServer(('', __port__), H)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
