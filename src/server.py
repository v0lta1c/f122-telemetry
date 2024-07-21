from http.server import BaseHTTPRequestHandler, HTTPServer
import shared
import json
import select

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self, status_code=200):
        self.send_response(status_code);
        self.send_header('Content-type', 'application/json');
        self.end_headers();

    def do_GET(self):
        if self.path == "/api/test":
            self._set_response();
            response = "HELLO RACERS!";
            self.wfile.write(json.dumps(response).encode('utf-8'));
        elif self.path == "/api/raceData":
            self._set_response();
            jsonDumpFile = shared.get_json_dump_file();
            self.wfile.write(json.dumps(jsonDumpFile).encode('utf-8'));
        else:
            self._set_response(404);
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode('utf-8'));

    def do_POST(self):
        if self.path == "/api/fastest-lap":
            pass


class HTTPServerHandler(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, stop_event):
        super().__init__(server_address, RequestHandlerClass);
        self.stop_event = stop_event;

    def serve_forever(self, poll_interval=0.5):
        while not self.stop_event.is_set():
            rlist, _, _ = select.select([self], [], [], poll_interval)
            if rlist:
                self.handle_request()

def run_server(stop_event=None):
    port = 8000;
    server_address = ('', port);
    httpd = HTTPServerHandler(server_address, HTTPRequestHandler, stop_event)
    print(f'Starting http server on port {port}...');
    httpd.serve_forever(); 
    print(f'Stopping the http server.......');