from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class H(BaseHTTPRequestHandler):
    _cs_ports=[]
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("4c44ed6d-4b46-4093-93f1-6b29a95e08ea")
        for p in self._cs_ports:
            self.wfile.write(";127.0.0.1:8897,%(p)d,8896" % vars())
        self.wfile.write("\n")

def run(port, cs_ports):
    H._cs_ports = cs_ports
    try:
        server = HTTPServer(('', port), H)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
