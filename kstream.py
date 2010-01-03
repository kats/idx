import httplib, urllib, string
import re

def open(uri):
    return kstream(uri)

def __parse_url(uri):
    scheme = netloc = path = port = "" 
    # scheme
    i = string.find(uri, "://")
    if i > 0:
        scheme, uri = string.lower(uri[:i]), uri[i+3:]
    # netloc
    i = string.find(uri, "/")
    if i > 0:
        netloc, uri = string.lower(uri[:i]), uri[i+1:]
    # port
    i = string.find(netloc, ":")
    if i > 0:
        netloc, port = netloc[:i], netloc[i+1:]
    
    return scheme, netloc, port, uri

# TODO (kats): DNS cache in module.
# TODO (kats): isolate master response parsing code
class kstream:
    "Reads files from Kanso in lazy forward-only manner."

    def __init__(self, uri):
        "uri: kanso://<master-location>[:port]/<full-file-name>"
        self.off = 0
        self.uri = uri

    def get_next_chunk_loc(self):
        scheme, netloc, port, path = _parse_url(self.uri)
        if scheme != "kanso": raise "unknown scheme, use kanso://"
        conn = httplib.HTTPConnection(netloc, port)
        params = urllib.urlencode({"method":"read", "offset":self.off})
        conn.request("GET", "/" + path + "?" + params)
        resp = str(conn.getresponse().read()).split(";")
        return (resp[0], resp[1:])

    def read_chunk(self, chunk_id, servers):
        for server in random.shuffle(servers):
            server = server.split(":")
            try:
                conn = httplib.HTTPConnection(server[0], server[1].split(",")[1])
                conn.request("GET", "/" + chunk_id)
                return conn.getresponse()
            except: pass

    def read(self):
        (chunk_id, servers) = self.get_next_chunk_loc()
        return self.read_chunk(chunk_id, servers).read()
