import httplib, urllib 

class kstream:
	def __init__(self, filename):
		self.off = 0
		self.filename = filename

	def get_next_chunk_loc(self):
		conn = httplib.HTTPConnection("kanso-master.kepref.kontur", 22222)
		params = urllib.urlencode({"method":"read", "offset":self.off})
		conn.request("GET", "/" + self.filename + "?" + params)
		resp = str(conn.getresponse().read()).split(";")
		return (resp[0], resp[1:])

	def read_chunk(self, chunk_id, servers):
		server = servers[0].split(":")
		conn = httplib.HTTPConnection(server[0], server[1].split(",")[1])
		conn.request("GET", "/" + chunk_id)
		return conn.getresponse()

	def read(self):
		(chunk_id, servers) = self.get_next_chunk_loc()
		return self.read_chunk(chunk_id, servers).read()
