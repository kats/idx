#!/usr/bin/env python
#-*- coding: utf-8 -*-

from collections import namedtuple
from uuid import uuid4
from struct import pack, pack_into, unpack_from
from read_structs import read_structs, TxnHead, Doc, Sign

#TxnHead = namedtuple("TxnHead", "orgId dcId time type upfrCode accYear provId corrType")
#Doc = namedtuple("Doc", "id type formKey documentFlags fileName kansoOffset contentLen")
#Sign = namedtuple("Sign", "id docId type kansoOffset contentLen")

def __write_head(h):
    layout = "=16s16sQib" 
    l = len(h.upfrCode)
    b = "====" + pack(layout, h.orgId.bytes_le, h.dcId.bytes_le, h.time, h.type, l)
    layout = "=" + str(l) + "siii"
    return b + pack(layout, h.upfrCode, h.accYear, h.provId, h.corrType)

def __write_doc(d):
    layout = "=i16siiib"
    l = len(d.fileName)
    b = pack(layout, 1, d.id.bytes_le, d.type, d.formKey, d.documentFlags, l)
    layout = "=" + str(l) + "sqi"
    return b + pack(layout, d.fileName, d.kansoOffset, d.contentLen)

def __write_sign(s):
    layout = "=i16s16siqi"
    return pack(layout, 1, s.id.bytes_le, s.docId.bytes_le, s.type, s.kansoOffset, s.contentLen)

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

def write_struct(head, doc, sign):
    b = __write_head(head) + __write_doc(doc) + __write_sign(sign)
    b = b + pack("=i", __hash(b))
    return b

# for testing, remove this
if __name__ == "__main__":
    txnHead = TxnHead(uuid4(), uuid4(), 0, 1, "1234567", 2000, 2, 3)
    doc = Doc(uuid4(), 1, 2, 3, "preved", 10101010, 777)
    sign = Sign(uuid4(), uuid4(), 10, 20202020, 888)

    bin = open("bin", "ab")
    b = write_struct(txnHead, doc, sign)
    bin.write(b)
    bin.close()

    bin = open("bin", "rb")
    for t in read_structs(bin.read()):
        print t
