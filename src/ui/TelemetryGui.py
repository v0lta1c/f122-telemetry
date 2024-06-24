import tkinter as tk
from tkinter import ttk
import socket
import threading
import sys

from telemetry.Telmetry import Telemetry

class TelemetryGui:
    def __init__(self, root, discord_enabled, session_data, show_main_window_callback):
        self.capture_window = tk.Toplevel(root);
        self.capture_window.title("F1 22 Telemetry");

        self.show_main_window_callback = show_main_window_callback;
        self.discord_enabled = discord_enabled;
        self.session_data = session_data;

        # Create an instance for telemetry
        self.telemetry = Telemetry();

        # Display session type and track name
        session_label = ttk.Label(self.capture_window, text=f"Session Type:");
        session_label.grid(row=0, column=0, columnspan=2, pady=10);

        track_label = ttk.Label(self.capture_window, text=f"Track Name:");
        track_label.grid(row=1, column=0, columnspan=2, pady=10);

        # Create the table headers
        headers = ["Player ID", "Name", "Position", "Lap Time", "Pit"];
        for col, header in enumerate(headers):
            header_label = ttk.Label(self.capture_window, text=header)
            header_label.grid(row=2, column=col, padx=5, pady=5);

        self.table_rows = [];

        #Create a frame for the table rows
        self.table_frame = ttk.Frame(self.capture_window);
        self.table_frame.grid(row=3, column=0, columnspan=5, pady=10);

        # Add a stop Capture button
        stop_button = ttk.Button(self.capture_window, text="Stop Capture", command=self.stop_capture);
        stop_button.grid(row=4, column=0, columnspan=2, pady=10);
    
        # Start the socket listener for telemetry data
        self.telemetry.start(discord_enabled=self.discord_enabled);

        # Handle the window close event
        self.capture_window.protocol("WM_DELETE_WINDOW", self.quit_application);

    def update_table(self, data):

        # First we empty the rows table
        for row in self.table_rows:
            for widget in row:
                widget.destroy();
        self.table_rows.clear();

        for i, player in enumerate(data):
            player_id, name, position, laptime, pit = player;
            row_widgets = [];
            for col, value in enumerate(player):
                label = ttk.Label(self.table_frame, text=value);
                label.grid(row=1, column=col, padx=5, pady=5);
                row_widgets.append(row_widgets);

    def stop_capture(self):
        self.telemetry.stop();
        self.capture_window.destroy();
        print("Stop Capture");
        self.show_main_window_callback();
    
    def quit_application(self):
        self.stop_capture();
        sys.exit();