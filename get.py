from uuid import UUID
from struct import unpack_from, calcsize
from kstream import *
from read_structs import read_structs

for txn in read_structs(kstream("kanso://kanso-master.kepref.kontur/pfr/transactions").read()):
	print txn
