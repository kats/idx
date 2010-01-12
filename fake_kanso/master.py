from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import config

class H(BaseHTTPRequestHandler):
    _cs_ports=[]
    def do_GET(self):
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
