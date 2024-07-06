import sys
from typing import Dict, Any

from PySide6 import QtCore
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QGridLayout, QFrame
from PySide6.QtGui import QFontDatabase, QFont

from constants import Session_Type_Name, SessionType, Track_Names, TrackId, FONT_PATH
from telemetry.Telmetry import Telemetry
from ui.DriverHistoryGui import DriverHistoryGui
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
        self.telemetry = Telemetry(
            lap_change_callback=self.on_lap_changed,
            on_session_start=self.resetUIElementsIfOpen
        );
        self.telemetry.start(discord_enabled=self.discord_enabled);

        # Text for dropdown menu in the driver summary table
        self.driver_context_menu = {
            "Show Race History": self.printRaceHistory,
            "Show Pit and Tyre History": self.printPitTyreHistory
        };
        self.isSessionStarting = False;
    
        # Make a signal mapper to emit a signal when driver label is pressed in the summary
        self.signalMapper = QtCore.QSignalMapper(self);
        # Add a flag to make sure the handle window event is fired only once
        self.isDriverWindowOpen = False;
        self.openDriverWindows = {};

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
                self.table_labels[row][col].driver_position = row;
    
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
            header_label.setToolTip("Hallo, ich bin text");

            self.header_labels.append(header_label);
    
        # Create empty table rows
        for row in range(self.telemetry.total_num_cars):
            row_labels = [];
            for col in range(len(headers)):
                label = ClickableLabel("");
                label.setAlignment(QtCore.Qt.AlignCenter);
                label.setFont(self.custom_font);
                self.table_layout.addWidget(label, row, col);
                row_labels.append(label);
                label.setToolTip("Kilkkaa tästää!");
                label.rightClicked.connect(self.handleLabelRightClick);
                #self.signalMapper.setMapping(label, row);
            self.table_labels.append(row_labels);

            #self.signalMapper.mappedInt.connect(self.handleLabelRightClick);
    
            # Calculate width based on sample data
            sample_data_width = len("Sample Data") * 8;
            max_cell_width = max(max_cell_width, sample_data_width);

        # Set column minimum width for table cells
        for col in range(len(headers)):
            self.header_layout.setColumnMinimumWidth(col, max_header_width);
            self.table_layout.setColumnMinimumWidth(col, max_cell_width);

    def printRaceHistory(self, driver_position: int):
        driver_id = None;
        name = None;

        for id in range(self.telemetry.total_num_cars):
            if self.telemetry.laptime_data.get_lapdata_value_from_key(id)['m_carPosition'] == driver_position + 1:
                driver_id = id;
                name = self.telemetry.getDriverNameFromId(driver_id);
                break;
        
        if driver_id is not None:
            driver_data = self.telemetry.driverSummary.getDriverSummary(driver_id);
            if driver_id not in self.openDriverWindows:
                self.show_driver_info(driver_id, name, driver_data);

    def printPitTyreHistory(self, driver_position: int):
        pass

    @QtCore.Slot()
    def handleLabelRightClick(self):

        if isinstance(self.sender(), ClickableLabel):
            label: ClickableLabel = self.sender();
            driver_position: int = label.driver_position;
    
            label.setContextMenuActions(self.driver_context_menu);

            pos: QtCore.QPoint = label.rect().center();
            label.showContextMenu(pos, driver_position);        

    @QtCore.Slot(int)
    def handle_label_click(self, driverPosition: int):
        driver_id = None;
        name = None;

        for id in self.telemetry.total_num_cars:
            if self.telemetry.laptime_data.get_lapdata_value_from_key(id)['m_carPosition'] == driverPosition + 1:
                driver_id = id;
                name = self.telemetry.getDriverNameFromId(driver_id);
                break;
        
        if driver_id is not None:
            driver_data = self.telemetry.driverSummary.getDriverSummary(driver_id);
            if driver_id not in self.openDriverWindows:
                self.show_driver_info(driver_id, name, driver_data);
    
    @QtCore.Slot(dict)
    def update_driver_window(self,  new_data_dict: Dict[int, Dict[str, Any]]):
        driver_window = self.sender(); # returns the sender
        if driver_window:
            driver_window.update(new_data_dict);
    
    def on_lap_changed(self, driver_id: int):

        if driver_id in self.openDriverWindows:
            if self.isSessionStarting:
                driver_data = {};
                self.isSessionStarting = False;
            else:
                driver_data = self.telemetry.driverSummary.getDriverSummary(driver_id);
            
            self.openDriverWindows[driver_id].dataUpdated.emit(driver_data);
    
    def show_driver_info(self, driver_id: int, name: str, driver_data: Dict[int, Dict[str, Any]]):

        driver_info_window = DriverHistoryGui(driver_id, name, driver_data);
        driver_info_window.finished.connect(lambda: self.closeDriverInfo(driver_id));
        self.openDriverWindows[driver_id] = driver_info_window;
        driver_info_window.show();
    
    # Callback from telemetry, event fires whenever session is started to make sure all ui elements are empty
    def resetUIElementsIfOpen(self):
        for driver_id in range(self.telemetry.total_num_cars):
            if driver_id in self.openDriverWindows:
                self.isSessionStarting = True;
                self.on_lap_changed(driver_id);

    def closeDriverInfo(self, driver_id: int):

        if driver_id in self.openDriverWindows:
            self.openDriverWindows[driver_id].deleteLater();
            del self.openDriverWindows[driver_id];

    # Stop capturing the telemetry
    # TODO: Add this option to an API endpoint
    @QtCore.Slot()
    def stop_capture(self):
        self.telemetry.stop();
        self.close();
        # Transfer control to the main window
        self.show_main_window_callback();
    
    # Close the Application and exit
    def quit_application(self):
        self.stop_capture();
        sys.exit();