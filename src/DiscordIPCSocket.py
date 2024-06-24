import socket 
import threading
import time

from constants import IP_discordIPC, PORT_discordIPC

class DiscordIPCSocket:
    def __init__(self):
        self.ipc_socket = None;
        self.stop_event = threading.Event();

    def connect_to_ipc(self):
        try: 
            self.ipc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
            self.ipc_socket.connect((IP_discordIPC, PORT_discordIPC));
            print("Connected to the IPC Socket!");

            # Keep the connection alive
            while not self.stop_event.is_set():
                time.sleep(1);

        except ConnectionRefusedError:
            print("Failed to connect to the IPC: Connection Refused.\n Retrying in 5 seconds");
            time.sleep(5);

        except Exception as e:
            print(f'Error: Failed to send data over IPC: {e}');
    
    def start_ipc_socket_thread(self):
        self.socket_thread = threading.Thread(target=self.connect_to_ipc, daemon=True);
        self.socket_thread.start();
    
    def join_ipc_socket_thread(self):
        if self.socket_thread  is not None:
            self.stop_event.set();
            self.socket_thread.join();
    
        # Optionally close the IPC Socket

        if self.ipc_socket is not None:
            self.ipc_socket.close();

    def send_ipc_trigger(self, message: str) -> None:

        if self.ipc_socket is None:
            print("No IPC Connection Available");
            return
        
        try:
            self.ipc_socket.sendall(message.encode());
        except Exception as e:
            print(f'Error: Failed to send data over IPC: {e}');