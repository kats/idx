#!/usr/env/bin python

import kstream 

of = open("outfile", "wb+")
ks = kstream.open("kanso://kanso-master.kepref.kontur/pfr/test/transactions")
for b in ks.read():
    of.write(b)
of.close()
