from uuid import UUID
from struct import unpack_from, calcsize
from kstream import *
from read_structs import *

__label__ = "===="

# TODO (kats): bounds checking
def read_txn(buf, off):
	head, o = read_head(buf, off)
	docs, o = read_array(buf, o, read_doc)
	signs, o = read_array(buf, o, read_sign)

	if unpack_from("=i", buf, o)[0] == hash(buf[off:o]):
		off = o + 4
		return (off, (head, docs, signs))

def read_structs(buf, off=0):
	o = off
	while o < len(buf):
		# this double-checking is slightly faster
		if buf[o] != __label__[0] or buf[o:o+4] != __label__:
			o += 1
			continue

		res = read_txn(buf, o)
		if not res: 
			o += 1
			continue
		(o, txn) = res
		yield res[1]

from IndexServer import *
updater = IndexServerUpdater("index.sqlite")
for txn in read_structs(open("fake_kanso/chunks/4c44ed6d-4b46-4093-93f1-6b29a95e08ea", "rb").read()):
    #for txn in read_structs(kstream("-path-to-file-here-").read()):
    #	print txn
    updater.insert_record(txn)
    #print txn[0].orgId
updater.commit()
