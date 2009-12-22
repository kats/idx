from uuid import UUID
from collections import namedtuple
from struct import unpack_from, calcsize
from kstream import *

__label__ = "===="

def hash(bytes):
	h = 0x00000000
	l = len(bytes)
	for i in xrange(0, l-3, 4):
		h ^= unpack_from("i", bytes, i)[0]
	if l % 4 == 1:
		h ^= unpack_from("i", bytes+"\x00\x00\x00", l-1)[0]
	if l % 4 == 2:
		h ^= unpack_from("i", bytes+"\x00\x00", l-2)[0]
	if l % 4 == 3:
		h ^= unpack_from("i", bytes+"\x00", l-3)[0]
	return h

def read_sign(bytes, off):
	layout = "16s16siqi"
	Sign = namedtuple("Sign", "id docId type kansoOffset contentLen")
	s = unpack_from(layout, bytes, off)
	sign = Sign(UUID(bytes_le=s[0]), UUID(bytes_le=s[1]), *s[2:])
	return sign, off+calcsize(layout)

def read_doc(bytes, off):
	layout1 = "16siiB"
	Doc = namedtuple("Doc", "id type formKey fileName kansoOffset contentLen")
	d1 = unpack_from(layout1, bytes, off)
	d2 = unpack_from(str(d1[3])+"s", bytes, off+calcsize(layout1))
	d3 = unpack_from("qi", bytes, off+calcsize(layout1)+d1[3])
	doc = Doc(UUID(bytes_le=d1[0]), d1[1], d1[2], d2[0], d3[0], d3[1])
	return doc, off+calcsize(layout1)+calcsize("qi")+d1[3]

def read_structs(buf):
	layout = "16s16sQix7siii"
	TxnHead = namedtuple("TxnHead", "orgId dcId time type upfrCode accYear provId corrType")
	off = 0
	while off < len(buf)-4:
		if unpack_from("4s", buf, off)[0] != __label__: 
			off += 1
			continue
		innerOff = off + 4
		t = unpack_from(layout, buf, innerOff)
		txnHead = TxnHead(UUID(bytes_le=t[0]), UUID(bytes=t[1]), *t[2:8])
		innerOff += calcsize(layout)
		doc_count = unpack_from("i", buf, innerOff)[0]
		innerOff += 4
		docs = []
		if doc_count > 1000:
			off += 1
			continue
		for idoc in xrange(0, doc_count):
			doc, innerOff = read_doc(buf, innerOff)
			docs.append(doc)
		
		sign_count = unpack_from("i", buf, innerOff)[0]
		if sign_count > 1000: 
			off += 1
			continue
		innerOff += 4
		signs = []
		for isign in xrange(0, sign_count):
			sign, innerOff = read_sign(buf, innerOff)
			signs.append(sign)

		if unpack_from("i", buf, innerOff)[0] == hash(buf[off:innerOff]):
			off = innerOff + 4
			yield (txnHead, docs, signs)
		else: 
			off += 1

for txn in read_structs(kstream("pfr/transactions").read()):
	print txn[0].orgId
