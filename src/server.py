from http.server import BaseHTTPRequestHandler, HTTPServer
import shared
import json
import select
import requests
from websockets import WebSocketServerProtocol

from constants import webhook_IP, webhook_PORT
from typing import Dict, Any

# A set to store all the clients connected to the WebSocket
clients = set();

# Dict listing all the events connected to the WebSocket
event_data: Dict[str, Any] = {
    'fastest-lap': None,
    'pit-change': None,
    'time-penalty': None,
    'drive-through': None,
    'retirement': None,
    'raceData': None,
};

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
        elif self.path.startswith('/api/'):
            event_name = self.path[len('/api/'):];
            if event_name in event_data:
                if event_data[event_name]:
                    self._set_response();
                    self.wfile.write(json.dumps(event_data[event_name]).encode('utf-8'));
                else:
                    self._set_response(204); # No Content
            else:
                self._set_response(404); # Not Found
                self.wfile.write(json.dumps({'error': 'Not Found'}).encode('utf-8'));
        else:
            self._set_response(404);
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode('utf-8'));

class HTTPServerHandler(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, stop_event):
        super().__init__(server_address, RequestHandlerClass);
        self.stop_event = stop_event;

    def serve_forever(self, poll_interval=0.5):
        while not self.stop_event.is_set():
            rlist, _, _ = select.select([self], [], [], poll_interval)
            if rlist:
                self.handle_request();

# Start the HTTP server using this method
def run_server(stop_event=None):
    port = 8000;
    server_address = ('', port);
    httpd = HTTPServerHandler(server_address, HTTPRequestHandler, stop_event)
    print(f'Starting http server on port {port}...');
    httpd.serve_forever(); 
    print(f'Stopping the http server.......');

# This method generates a POST request and sends it to the webhook server at the appropriate IP and PORT
def send_to_webhook(event_name, data):
    webhook_url = "http://" + webhook_IP + ":" + str(webhook_PORT);
    payload = json.dumps({event_name: data});
    headers = {'Content-Type': 'application/json'};
    try:
        response = requests.post(webhook_url, data=payload, headers=headers, timeout=5);
    
        if response.status_code == 200:
            print(f'Successfully sent {event_name} update!');
        else:
            print(f'Faild to send {event_name} update, status code: {response.status_code}');
    
    except requests.Timeout:
        print("Request timed out :(");
    except Exception as e:
        print(f"Exception occured: {e}");

# Update WebSocket event
# This method is triggered whenever an event occurs in the game and sends it to the webhook server via a POST request
def update_event(event_name, data):
    event_data[event_name] = data;
    send_to_webhook(event_name=event_name, data=data);