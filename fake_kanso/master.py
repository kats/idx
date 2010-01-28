from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse, parse_qs
import config, const, files

def _where_read(path, offset):
    file = files.find_file(path)
    if not file: return
    (size, chunks) = file
    if offset >= size: return
    return chunks[offset/const.CHUNK_SIZE]


class H(BaseHTTPRequestHandler):
    _cs_ports=[]

    def get_offset(self, query):
        params = parse_qs(query)
        offset = 0
        if "offset" in params: 
            offset = int(params["offset"][0])
        return offset

    def do_GET(self):
        (s, l, path, p, query, f) = urlparse(self.path)
        chunk_id = _where_read(path, self.get_offset(query))

        if not chunk_id:
            self.send_response(400)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(chunk_id)
        for p in self._cs_ports:
#            self.wfile.write(";127.0.0.1:8897,%d,8896" % p)
            self.wfile.write(";10.0.1.4:8897,%d,8896" % p)
        self.wfile.write("\n")

def run(port, cs_ports):
    H._cs_ports = cs_ports
    try:
        server = HTTPServer(('', port), H)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
