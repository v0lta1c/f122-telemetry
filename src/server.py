from http.server import BaseHTTPRequestHandler, HTTPServer
import shared
import json

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

def run_server(server_class = HTTPServer, handler_class=HTTPRequestHandler, port=8000):
    server_address = ('', port);
    httpd = server_class(server_address, handler_class);
    print(f'Starting httpd server on port {port}...');
    httpd.serve_forever(); 

if '__name__' == '__main__':
    run_server();