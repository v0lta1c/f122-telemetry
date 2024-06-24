import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import time
import sys
from ui.TelemetryGui import TelemetryGui

from packets import ParticipantData, CarTelemetry, SessionData

class TelemetryApp:
    def __init__(self, root, car_telemetry_data: CarTelemetry, participant_data: ParticipantData, session_data: SessionData):
        self.root = root;
        self.root.title("F1 22 Telemetry");

        self.car_telemetry_data = car_telemetry_data;
        self.participant_data = participant_data;
        self.session_data = session_data;

        self.discord_enabled = tk.IntVar();

        # Create a frame for the window content
        frame = ttk.Frame(root, padding="10");
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S));

        # Add a label for "f1 22 telemetry"
        label = ttk.Label(frame, text="F1 22 Telemetry");
        label.grid(row=0, column=0, columnspan=2);

        # Add Start and Quit buttons
        start_button = ttk.Button(frame, text="Start", command=self.start_telemetry);
        start_button.grid(row=1, column=0, pady=10);

        quit_button = ttk.Button(frame, text="Quit", command=self.quit_application);
        quit_button.grid(row=1, column=1, pady=10);

        # Add a checkbox for the discord runtime argument
        checkbox = ttk.Checkbutton(frame, text="Enable Discord Bot?", variable=self.discord_enabled, command=self.enable_discord_bot);
        checkbox.grid(row=2, column=0, columnspan=2, pady=10);

        #Handle the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application);

    def quit_application(self):
        self.root.quit();
        self.root.destroy();
        sys.exit();

    def start_telemetry(self):
        self.root.withdraw(); # Hide the main window
        self.capture_window = TelemetryGui(self.root, self.discord_enabled.get(), self.session_data, self.show_main_window);
    def enable_discord_bot(self):
        pass

    def show_main_window(self):
        self.root.deiconify(); # Show the main window again

def run_gui(car_telemetry_data, participant_data, session_data):
    root = tk.Tk();
    app = TelemetryApp(root, car_telemetry_data, participant_data, session_data);
    root.mainloop();

