import os
from uuid import uuid4
import const

_files = {}
_chunks = {}

def add_file(local_name, kanso_name):
    file = open(local_name, "rb+")
    size = os.stat(local_name).st_size
    chunks = []
    for s in range(0, size, const.CHUNK_SIZE):
        chunk_id = str(uuid4())
        _chunks[chunk_id] = (file, s)
        chunks.append(chunk_id)
    _files[kanso_name] = (size, chunks)

def find_file(kanso_name):
    if kanso_name in _files: return _files[kanso_name]

def find_chunk(chunk_id):
    if chunk_id in _chunks: return _chunks[chunk_id]
