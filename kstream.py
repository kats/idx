import httplib, urllib, string
import re, random

def open(uri):
    return kstream(uri)

def _parse_url(uri):
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
        self.uri = uri

    def __locate_next_chunk(self, offset):
        scheme, host, port, path = _parse_url(self.uri)
        if scheme != "kanso": raise "unknown scheme, use kanso://"
        if port == "": port = 22222

        conn = httplib.HTTPConnection(host, port)
        params = urllib.urlencode({"method":"read", "offset":offset})
        conn.request("GET", "/" + path + "?" + params)
        resp = conn.getresponse()
        if resp.status != 200: # no more chunks
            return (None, None)
        s = str(resp.read()).split(";")
        return (s[0], s[1:])

    def __read_chunk(self, offset, chunk_id, servers):
        random.shuffle(servers)
        for server in servers:
            server = server.split(":")
            try:
                conn = httplib.HTTPConnection(server[0], server[1].split(",")[1])
                params = urllib.urlencode({"offset":offset})
                conn.request("GET", "/" + chunk_id + "?" + params)
                resp = conn.getresponse()
                if resp.status == 200:
                    return resp.read()
            except: pass

    def read(self, offset=0):
        while True:
            (chunk_id, servers) = self.__locate_next_chunk(offset)
            if not chunk_id:
                break
            inner_offset = offset % (64*1024*1024)
            chunk = self.__read_chunk(inner_offset, chunk_id, servers)
            if not chunk: break
            offset += len(chunk)
            yield chunk
