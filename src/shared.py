import threading
from typing import Dict

lock = threading.Lock();
jsonDumpFile = [];
fastest_lap_payload: Dict = {};

def get_json_dump_file():
    with lock:
        return jsonDumpFile.copy();

def update_json_dump_file(data):
    with lock:
        jsonDumpFile[:] = data;