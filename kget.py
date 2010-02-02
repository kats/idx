#!/usr/env/bin python

import kstream 

of = open("outfile", "wb+")
ks = kstream.open("kanso://localhost/pfr/test/content")
for b in ks.read():
    of.write(b)
of.close()
