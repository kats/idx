import chunkserver, master
from threading import *

__all__ = ["run"]

def _run_chunkserver(port):
    ct = Thread(target=chunkserver.run, args=(port,))
    ct.daemon = True
    ct.start()

def _run_master(port, cs_ports):
    ct = Thread(target=master.run, args=(port, cs_ports))
    ct.daemon = True
    ct.start()

def run(master_port=22222, cs_count=3):
    cs_ports = xrange(8001, 8001+cs_count)
    for port in cs_ports:
        _run_chunkserver(port)
    _run_master(master_port, cs_ports)
