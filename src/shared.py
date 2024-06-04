import threading

lock = threading.Lock();
jsonDumpFile = [];

def get_json_dump_file():
    with lock:
        return jsonDumpFile.copy();

def update_json_dump_file(data):
    with lock:
        jsonDumpFile[:] = data;