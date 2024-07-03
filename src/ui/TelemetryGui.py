import sys
from typing import Dict, Any

from PySide6 import QtCore
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QGridLayout, QFrame
from PySide6.QtGui import QFontDatabase, QFont

from constants import Session_Type_Name, SessionType, Track_Names, TrackId, FONT_PATH
from telemetry.Telmetry import Telemetry
from ui.components.ClickableLabel import ClickableLabel

class TelemetryGui(QWidget):
    def __init__(self, parent=None, discord_enabled=False, show_main_window_callback=None):
        super().__init__(parent);
        self.setWindowTitle("F1 22 Telemetry");
        self.show_main_window_callback = show_main_window_callback;
        self.discord_enabled = discord_enabled;

        font_id = QFontDatabase.addApplicationFont(FONT_PATH);
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0];
            self.custom_font = QFont(font_family);
        else:
            print("Failed to load the custom font");
            self.custom_font = self.font(); # Revert to original font

        self.session_type = QLabel("Session Type: Session Not Detected");
        self.track_name = QLabel("Track Name: Session Not Detected");

        self.session_type.setAlignment(QtCore.Qt.AlignCenter);
        self.session_type.setFont(self.custom_font);
        self.track_name.setAlignment(QtCore.Qt.AlignCenter);
        self.track_name.setFont(self.custom_font);

        self.header_frame = QFrame();
        self.header_layout = QGridLayout(self.header_frame);
        self.header_layout.setContentsMargins(5, 10, 5, 10);
        
        self.table_frame = QFrame();
        self.table_layout = QGridLayout(self.table_frame);
        self.table_layout.setContentsMargins(5, 10, 5, 10);

        self.header_labels = [];
        self.table_labels = [];

        self.detailed_information_button = QPushButton("Detailed Information");
        self.stop_capture_button = QPushButton("Stop Capture");
        self.stop_capture_button.clicked.connect(self.stop_capture);

        self.detailed_information_button.setFont(self.custom_font);
        self.stop_capture_button.setFont(self.custom_font);

        main_layout = QVBoxLayout(self);
        main_layout.addWidget(self.session_type);
        main_layout.addWidget(self.track_name);
        main_layout.addWidget(self.header_frame);
        main_layout.addWidget(self.table_frame);
        main_layout.addWidget(self.detailed_information_button);
        main_layout.addWidget(self.stop_capture_button);

        # Create an instance for telemetry
        self.telemetry = Telemetry(real_time_callback=self.update_real_time_summary);
        self.telemetry.start(discord_enabled=self.discord_enabled);
    
        self.initialize_summary_table_widgets([]);

        # Initialize and start a timer to call update_gui every 5 seconds
        self.timer = QtCore.QTimer(self);
        self.timer.timeout.connect(self.update_gui);
        self.timer.start(5000);

        self.show();

    # Updates the gui at a fixed interval with the new inforation from the telemetry
    def update_gui(self):

        if(self.telemetry.inSession and self.telemetry.running):
            driver_dict = self.telemetry.get_latest_summary_data(); # Get the summary data in a dict from telemetry
            if driver_dict is not None:
                self.update_real_time_summary(driver_dict); # Update the summary

    # Keeps the main table of the GUI updated with real time
    def update_real_time_summary(self, data_dict: Dict[int, Dict[str, Any]]):

        if data_dict is None: return;
        if len(data_dict) < 1: return;
    
        # Initialize the headers if they haven't been created
        if not self.header_labels:
            headers = list(next(iter(data_dict.values())).keys());
            self.initialize_summary_table_widgets(headers);
        
        # Generate the rows for the table based on available total cars
        for row, (driver_id, driver_data) in enumerate(data_dict.items()):
            # Ensure there are enough rows in the table
            for col, value in enumerate(driver_data.values()):
                self.table_labels[row][col].setText(str(value));
    
        # Update session type and track name
        session_type_name = Session_Type_Name.get(SessionType(self.telemetry.session_data.get_session_data_from_key("m_sessionType")).value)
        track_name = Track_Names.get(TrackId(self.telemetry.session_data.get_session_data_from_key("m_trackId")).value);
        self.session_type.setText(f"Session Type: {session_type_name}");
        self.track_name.setText(f"Track Name: {track_name}");

    def initialize_summary_table_widgets(self, headers):

        # Clear Existing Widgets
        for label in self.header_labels:
            label.deleteLater();
    
        for row_labels in self.table_labels:
            for label in row_labels:
                label.deleteLater();
    
        self.header_labels.clear();
        self.table_labels.clear();
    
        max_header_width = 0;
        max_cell_width = 0;

        # Create new headers:
        for col, header in enumerate(headers):
            header_label = QLabel(header);
            header_label.setAlignment(QtCore.Qt.AlignCenter);
            header_label.setFont(self.custom_font);
            self.header_layout.addWidget(header_label, 0, col);

            # Calculate width based on header text length
            header_width = len(header) * 8;
            max_header_width = max(max_header_width, header_width);

            # Set column minimum width for headers
            self.header_layout.setColumnMinimumWidth(col, max_header_width);
            #header_label.setToolTip("Hallo, ich bin text");

            self.header_labels.append(header_label);
    
        # Create empty table rows
        for row in range(self.telemetry.total_num_cars):
            row_labels = [];
            for col in range(len(headers)):
                label = QLabel("");
                label.setAlignment(QtCore.Qt.AlignCenter);
                label.setFont(self.custom_font);
                self.table_layout.addWidget(label, row, col);
                row_labels.append(label);
            self.table_labels.append(row_labels);
    
            # Calculate width based on sample data
            sample_data_width = len("Sample Data") * 8;
            max_cell_width = max(max_cell_width, sample_data_width);
        
            #label.setToolTip("Kilkkaa tästää!");
        
            # Connect the signal from the clickable label
            #label.clicked.connect(self.load_driver_history_window);

        # Set column minimum width for table cells
        for col in range(len(headers)):
            self.header_layout.setColumnMinimumWidth(col, max_header_width);
            self.table_layout.setColumnMinimumWidth(col, max_cell_width);
    
    @QtCore.Slot()
    def load_driver_history_window(self):
        pass

    # Stop capturing the telemetry
    # TODO: Add this option to an API endpoint
    @QtCore.Slot()
    def stop_capture(self):
        self.telemetry.stop();
        self.close();
        print("Stop Capture");
        # Transfer control to the main window
        self.show_main_window_callback();
    
    # Close the Application and exit
    def quit_application(self):
        self.stop_capture();
        sys.exit();