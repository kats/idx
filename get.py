from uuid import UUID
from struct import unpack_from, calcsize
from kstream import *
from read_structs import read_structs
from IndexServer import *

import datetime

print datetime.datetime.now()

updater = IndexServerUpdater("index.sqlite")
for txn in read_structs(open("fake_kanso/chunks/4c44ed6d-4b46-4093-93f1-6b29a95e08ea", "rb").read()):
    updater.insert_record(txn)
updater.commit()

print datetime.datetime.now()
