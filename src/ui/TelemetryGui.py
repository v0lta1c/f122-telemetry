import tkinter as tk
from tkinter import ttk
import socket
import sys
from typing import Dict, Any

from constants import *
from telemetry.Telmetry import Telemetry

class TelemetryGui:
    def __init__(self, root, discord_enabled, show_main_window_callback):
        self.capture_window = tk.Toplevel(root);
        self.capture_window.title("F1 22 Telemetry");

        self.show_main_window_callback = show_main_window_callback;
        self.discord_enabled = discord_enabled;

        self.session_type = tk.StringVar();
        self.track_name = tk.StringVar();

        # Display session type and track name
        self.session_type.set("Session Type: Session Not Detected");
        self.track_name.set("Track Name: Session Not Detected");

        session_label = ttk.Label(self.capture_window, textvariable=self.session_type);
        session_label.grid(row=0, column=0, columnspan=2, pady=10);

        track_label = ttk.Label(self.capture_window, textvariable=self.track_name);
        track_label.grid(row=1, column=0, columnspan=2, pady=10);

        self.header_frame = ttk.Frame(self.capture_window);
        self.header_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=10);

        #Create a frame for the table rows
        self.table_frame = ttk.Frame(self.capture_window);
        self.table_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=10);

        self.header_labels = [];
        self.table_labels = [];

        # Add a detailed information button
        self.detailed_information_button = ttk.Button(self.capture_window, text="Detailed Information");
        self.detailed_information_button.grid(row=4, column=0, columnspan=2, pady=10);

        # Add a stop Capture button
        stop_button = ttk.Button(self.capture_window, text="Stop Capture", command=self.stop_capture);
        stop_button.grid(row=4, column=2, columnspan=2, pady=10);

        # Handle the window close event
        self.capture_window.protocol("WM_DELETE_WINDOW", self.quit_application);
    
        # Create an instance for telemetry
        self.telemetry = Telemetry(real_time_callback=self.update_real_time_summary);
        self.telemetry.start(discord_enabled=self.discord_enabled);

    # Keeps the main table of the GUI updated with real time
    def update_real_time_summary(self, data_dict: Dict[int, Dict[str, Any]]):

        if data_dict is None: return;
        if len(data_dict) < 1: return;
    
        if not self.header_labels:
            headers = list(next(iter(data_dict.values())).keys());
            self.initialize_summary_table_widgets(headers);
        
        for row, (driver_id, driver_data) in enumerate(data_dict.items()):
            for col, value in enumerate(driver_data.values()):
                self.table_labels[row][col].config(text=value);
    
        self.session_type.set(Session_Type_Name.get(SessionType(self.telemetry.session_data.get_session_data_from_key("m_sessionType")).value));
        self.track_name.set(Track_Names.get(TrackId(self.telemetry.session_data.get_session_data_from_key("m_trackId")).value));

    def initialize_summary_table_widgets(self, headers):

        # First we create the headers
        for col, header in enumerate(headers):
            header_label = ttk.Label(self.header_frame, text=header, width=15, anchor=tk.CENTER);
            header_label.grid(row=0, column=col, padx=5, pady=5);
            self.header_labels.append(header_label);
    
        # Now we create the rows with empty labels
        for row in range(self.telemetry.total_num_cars):
            row_labels = [];
            for col in range(len(headers)):
                label = ttk.Label(self.table_frame, text="", width=15, anchor=tk.CENTER);
                label.grid(row=row + 1, column=col, padx=5, pady=5);
                row_labels.append(label);
            self.table_labels.append(row_labels);

    def stop_capture(self):
        self.telemetry.stop();
        self.capture_window.destroy();
        print("Stop Capture");
        self.show_main_window_callback();
    
    def quit_application(self):
        self.stop_capture();
        sys.exit();