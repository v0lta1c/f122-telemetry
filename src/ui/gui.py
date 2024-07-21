import sys
import threading

from PySide6 import  QtGui
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QCheckBox
from PySide6.QtCore import Slot

from ui.TelemetryGui import TelemetryGui
from server import run_server

from packets import ParticipantData, CarTelemetry, SessionData
from constants import FONT_PATH

class TelemetryApp(QWidget):
    def __init__(self):
        super().__init__();
        self.setWindowTitle("F1 22 Telemetry");

        self.discordEnabled = False;    # To check whether discord bot is to be added or not

        # Add custom font
        font_id = QtGui.QFontDatabase.addApplicationFont(FONT_PATH);
        if font_id != -1:
            font_family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0];
            self.custom_font = QtGui.QFont(font_family);
        else:
            print("Failed to load the custom font");
            self.custom_font = self.font(); # Revert to original font

        # Create the widgets here
        self.label = QLabel('F1 22 Telemetry', self);
        self.start_button = QPushButton('Start', self);
        self.quit_button = QPushButton('Quit', self);
        self.checkbox = QCheckBox('Enable Discord Bot?', self);

        self.label.setFont(self.custom_font);
        self.start_button.setFont(self.custom_font);
        self.quit_button.setFont(self.custom_font);
        self.checkbox.setFont(self.custom_font);

        # Set their layout
        layout = QVBoxLayout(self);
        layout.addWidget(self.label);
        layout.addWidget(self.start_button);
        layout.addWidget(self.quit_button);
        layout.addWidget(self.checkbox);
        self.setLayout(layout);

        # Connect signals
        self.start_button.clicked.connect(self.start_telemetry);
        self.quit_button.clicked.connect(self.quit_application);
        self.checkbox.stateChanged.connect(self.enable_discord_bot);
    
        self.server_stop_event = threading.Event();
        self.start_server();

    @Slot()
    def quit_application(self):

        self.server_stop_event.set();
        if self.server_thread:
            self.server_thread.join();
        
        self.close();

    @Slot()
    def start_telemetry(self):
        self.hide(); # Hide the main window
        self.capture_window = TelemetryGui(discord_enabled=self.discordEnabled, show_main_window_callback=self.show_main_window);
        self.capture_window.show();
    
    @Slot()
    def enable_discord_bot(self):
        self.discordEnabled = self.checkbox.isChecked();

    def show_main_window(self):
        self.show();

    def start_server(self):
        self.server_thread = threading.Thread(target=run_server, args=(self.server_stop_event,), name="HTTP API Server",daemon=True);
        self.server_thread.start();

def run_gui():
    app = QApplication(sys.argv);
    ex = TelemetryApp();
    ex.show();
    sys.exit(app.exec());
