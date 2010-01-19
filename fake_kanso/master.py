from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse, parse_qs
import os
import config

class H(BaseHTTPRequestHandler):
    _cs_ports=[]
    def do_GET(self):
        (s, l, chunk, p, query, f) = urlparse(self.path)
        params = parse_qs(query)
        offset = 0
        if "offset" in params: 
            offset = int(params["offset"][0])

        chunk = config.FK_DIR + "/" + config.FK_FILENAME
        if offset >= os.stat(chunk).st_size:
            self.send_response(400)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(config.FK_FILENAME)
        for p in self._cs_ports:
            self.wfile.write(";127.0.0.1:8897,%d,8896" % p)
        self.wfile.write("\n")

def run(port, cs_ports):
    H._cs_ports = cs_ports
    try:
        server = HTTPServer(('', port), H)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
