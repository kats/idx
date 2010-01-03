from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from os import path
from sys import argv

class H(BaseHTTPRequestHandler):
    def do_GET(self):
		chunk = "fake_kanso/chunks" + self.path
		if not path.exists(chunk):
			self.send_response(404)
			self.end_headers()
		else:
			self.send_response(200)
			self.end_headers()
			self.wfile.write(open(chunk, "rb").read())

def run(port):
    server = HTTPServer(('', port), H)
    server.serve_forever()
