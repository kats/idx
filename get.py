import httplib, urllib, socket

class kstream:
	def __init__(self):
		self.off = 0

	def get_next_chunk_loc(self):
		conn = httplib.HTTPConnection("razr-kanso-master.kepref", 22222)
		params = urllib.urlencode({"method":"read", "offset":self.off})
		conn.request("GET", "/ReportsFinalInspProtocolMRIReceipt?" + params)
		resp = str(conn.getresponse().read()).split(";")
		return (resp[0], resp[1:])

	def read_chunk(self, chunk_id, servers):
		server = servers[0].split(":")
		conn = httplib.HTTPConnection(server[0], server[1].split(",")[0])
		conn.request("GET", "/" + chunk_id)
		return conn.getresponse()

	def read(self):
		(chunk_id, servers) = self.get_next_chunk_loc()
		return self.read_chunk(chunk_id, servers).read()


def open(file):
	return kstream()
	
print open(0).get_next_chunk_loc()
