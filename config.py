#!/usr/bin/env python
#-*- coding: utf-8 -*-

# File name to strore index DB.
IDX_FILENAME = "index.sqlite"
# Search server port.
# The '?orgId=<GUID>' param expected, where <GUID> is the string uesd in UUID.uuid(string) constructor.
IDX_WEBSERVER_PORT = 8092
# File URI with 'kanso://' namespace used to build index
KANSO_FILENAME = "kanso://127.0.0.1/pfr/test/transactions"
# Each time KANSO_FILENAME EOF reached we'll wait for KANSO_READ_UPDATES_DELAY secs
KANSO_READ_UPDATES_DELAY = 10 # in secs
# Index commited each time KANSO_FILENAME EOF reached and each IDX_ITEMS_PER_COMMIT.
IDX_ITEMS_PER_COMMIT = 50000
KANSO_MASTER_DEFAULT_PORT = 22222
IDX_DB_BUSY_DELAY = 0.5 # in secs
IDX_TRIALS = 3
