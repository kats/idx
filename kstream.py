import httplib, urllib, string

# TODO (kats): port
def _parse_url(url):
    scheme = netloc = path = query = "" 
    # scheme
    i = string.find(url, "://")
    if i > 0:
        scheme, url = string.lower(url[:i]), url[i+3:]
    # netloc
    i = string.find(url, "/")
    if i > 0:
        netloc, url = string.lower(url[:i]), url[i+1:]
    # path and query
    i = string.find(url, '?')
    if i >= 0:
        url, query = url[:i], url[i+1:]
    
    return scheme, netloc, url, query

class kstream:
    def __init__(self, filename):
        self.off = 0
        self.filename = filename

    def get_next_chunk_loc(self):
        scheme, netloc, url, query = _parse_url(self.filename)
        if scheme != "kanso": raise "wtf?"
        conn = httplib.HTTPConnection(netloc, 22222)
        params = urllib.urlencode({"method":"read", "offset":self.off})
        conn.request("GET", "/" + url + "?" + params)
        resp = str(conn.getresponse().read()).split(";")
        return (resp[0], resp[1:])

    # TODO (kats): random chunkserver
    def read_chunk(self, chunk_id, servers):
        server = servers[0].split(":")
        conn = httplib.HTTPConnection(server[0], server[1].split(",")[1])
        conn.request("GET", "/" + chunk_id)
        return conn.getresponse()

    def read(self):
        (chunk_id, servers) = self.get_next_chunk_loc()
        return self.read_chunk(chunk_id, servers).read()
