import chunkserver, master, config, const
from threading import *

__all__ = ["run", "add_file"]

def _run_chunkserver(port):
    ct = Thread(target=chunkserver.run, args=(port,))
    ct.daemon = True
    ct.start()

def _run_master(port, cs_ports):
    ct = Thread(target=master.run, args=(port, cs_ports))
    ct.daemon = True
    ct.start()

def run(master_port=config.MASTER_DEFAULT_PORT, cs_count=3):
    cs_ports = xrange(config.CS_PORT_RANGE_START, config.CS_PORT_RANGE_START + cs_count)
    for port in cs_ports:
        _run_chunkserver(port)
    _run_master(master_port, cs_ports)

def add_file(local_name, kanso_name):
    files.add_file(local_name, kanso_name)
