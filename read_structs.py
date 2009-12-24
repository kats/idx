from struct import unpack_from, calcsize
from collections import namedtuple
from uuid import UUID

TxnHead = namedtuple("TxnHead", "orgId dcId time type upfrCode accYear provId corrType")
Doc = namedtuple("Doc", "id type formKey fileName kansoOffset contentLen")
Sign = namedtuple("Sign", "id docId type kansoOffset contentLen")

def __hash(bytes):
	h = 0x00000000
	l = len(bytes)
	for i in xrange(0, l-3, 4):
		h ^= unpack_from("=i", bytes, i)[0]
	if l % 4 == 1:
		h ^= unpack_from("=i", bytes+"\x00\x00\x00", l-1)[0]
	if l % 4 == 2:
		h ^= unpack_from("=i", bytes+"\x00\x00", l-2)[0]
	if l % 4 == 3:
		h ^= unpack_from("=i", bytes+"\x00", l-3)[0]
	return h

def __read_head(buf, off):
	layout = "=4x16s16sQix7siii"
	t = unpack_from(layout, buf, off)
	head = TxnHead(UUID(bytes_le=t[0]), UUID(bytes_le=t[1]), *t[2:8])
	return head, off + calcsize(layout)

def __read_sign(bytes, off):
	layout = "=16s16siqi"
	s = unpack_from(layout, bytes, off)
	sign = Sign(UUID(bytes_le=s[0]), UUID(bytes_le=s[1]), *s[2:])
	return sign, off+calcsize(layout)

def __read_doc(bytes, off):
	layout1 = "=16siiB"
	d1 = unpack_from(layout1, bytes, off)
	d2 = unpack_from("="+str(d1[3])+"s", bytes, off+calcsize(layout1))
	d3 = unpack_from("=qi", bytes, off+calcsize(layout1)+d1[3])
	doc = Doc(UUID(bytes_le=d1[0]), d1[1], d1[2], d2[0], d3[0], d3[1])
	return doc, off+calcsize(layout1)+calcsize("=qi")+d1[3]

def __read_array(buf, off, read_fn):
	c = unpack_from("=i", buf, off)[0]
	o = off + 4
	elems = []
	for i in xrange(0, c):
		elem, o = read_fn(buf, o)
		elems.append(elem)
	return elems, o

# TODO (kats): bounds checking
def __read_txn(buf, off):
	head, o = __read_head(buf, off)
	docs, o = __read_array(buf, o, __read_doc)
	signs, o = __read_array(buf, o, __read_sign)

	if unpack_from("=i", buf, o)[0] == __hash(buf[off:o]):
		off = o + 4
		return (off, (head, docs, signs))

__label = "===="
def read_structs(buf, off=0):
	o = off
	while o < len(buf):
		# this double-checking is slightly faster
		if buf[o] != __label[0] or buf[o:o+4] != __label:
			o += 1
			continue

		res = __read_txn(buf, o)
		if not res: 
			o += 1
			continue
		(o, txn) = res
		yield res[1]
