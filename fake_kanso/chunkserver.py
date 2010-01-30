from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse, parse_qs
import config, const, files

class H(BaseHTTPRequestHandler):
    def get_params(self, query):
        params = parse_qs(query)
        offset = 0
        size = -1
        if "count" in params: 
            size = int(params["count"][0])
        if "offset" in params: 
            offset = int(params["offset"][0])
        return (offset, size)

    def do_GET(self):
        (s, l, chunk_id, p, query, f) = urlparse(self.path)
        chunk = files.find_chunk(chunk_id[1:])

        if not chunk:
            self.send_response(404)
            self.end_headers()
            return

        (file, offset) = chunk
        (inner_offset, size) = self.get_params(query)

        self.send_response(200)
        self.end_headers()
        file.seek(offset + inner_offset)
        if size < 0: 
            size = const.CHUNK_SIZE - inner_offset
        self.wfile.write(file.read(size))

def run(port):
    server = HTTPServer(('', port), H)
    server.serve_forever()
