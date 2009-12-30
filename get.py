from uuid import UUID
from struct import unpack_from, calcsize
from kstream import *
from read_structs import read_structs
from IndexServer import *

updater = IndexServerUpdater("index.sqlite")

#for txn in read_structs(open("fake_kanso/chunks/4c44ed6d-4b46-4093-93f1-6b29a95e08ea", "rb").read()):
for txn in read_structs(kstream("kanso://kanso-master.kepref.kontur/pfr/test/transactions").read()):
    updater.insert_record(txn)
updater.commit()

