import chunkserver, master
import os
from threading import *

__all__ = ["run", "append"]

def _run_chunkserver(port):
    ct = Thread(target=chunkserver.run, args=(port,))
    ct.daemon = True
    ct.start()

def _run_master(port, cs_ports):
    ct = Thread(target=master.run, args=(port, cs_ports))
    ct.daemon = True
    ct.start()

piece_size = 50*1024
cur = "fake_kanso/chunks/4c44ed6d-4b46-4093-93f1-6b29a95e08ea"
full = cur + ".full"

def run(master_port=22222, cs_count=3):
    open(cur, "w+").close()
    cs_ports = xrange(8001, 8001+cs_count)
    for port in cs_ports:
        _run_chunkserver(port)
    _run_master(master_port, cs_ports)

def append():
    cur_size = os.path.getsize(cur)
    full_size = os.path.getsize(full)
    if cur_size >= full_size: 
        return False
    cur_file = open(cur, "ab")
    full_file = open(full, "rb")
    full_file.read(cur_size)
    cur_file.write(full_file.read(piece_size))
    cur_file.close()
    full_file.close()
    return True


