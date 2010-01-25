from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse, parse_qs
import config, files

class H(BaseHTTPRequestHandler):
    def get_offset(self, query):
        params = parse_qs(query)
        offset = 0
        if "offset" in params: 
            offset = int(params["offset"][0])
        return offset

    def do_GET(self):
        (s, l, chunk_id, p, query, f) = urlparse(self.path)
        chunk = files.find_chunk(chunk_id)

        if not chunk
            self.send_response(404)
            self.end_headers()
            return

        (file, offset) = chunk
        inner_offset = get_offset(query)

        self.send_response(200)
        self.end_headers()
        file.seek(offset + inner_offset)
        self.wfile.write(file.read(const.CHUNK_SIZE - inner_offset))

def run(port):
    server = HTTPServer(('', port), H)
    server.serve_forever()
