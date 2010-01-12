import chunkserver, master
import os
from threading import *
import config

__all__ = ["run", "append"]

def _run_chunkserver(port):
    ct = Thread(target=chunkserver.run, args=(port,))
    ct.daemon = True
    ct.start()

def _run_master(port, cs_ports):
    ct = Thread(target=master.run, args=(port, cs_ports))
    ct.daemon = True
    ct.start()

piece_size = config.FK_CHANK_SIZE
cur = config.FK_DIR + '/' + config.FK_FILENAME
full = cur + ".full"

def run(master_port=config.FK_MASTER_DEFAULT_PORT, cs_count=3):
    open(cur, "w+").close()
    cs_ports = xrange(config.FK_CS_PORT_RANGE_START, \
            config.FK_CS_PORT_RANGE_START+cs_count)
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


