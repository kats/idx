from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from os import path
from sys import argv
from urlparse import urlparse, parse_qs

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        (s, l, chunk, p, query, f) = urlparse(self.path)
        params = parse_qs(query)
        offset = 0
        if "offset" in params: 
            offset = int(params["offset"][0])
        chunk = "fake_kanso/chunks" + chunk
        if not path.exists(chunk):
            self.send_response(404)
            self.end_headers()
        else:
            self.send_response(200)
            self.end_headers()
            f = open(chunk, "rb")
            f.read(offset)
            self.wfile.write(f.read())
            f.close()

def run(port):
    server = HTTPServer(('', port), H)
    server.serve_forever()
