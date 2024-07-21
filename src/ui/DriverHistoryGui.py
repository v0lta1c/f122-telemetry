from typing import Dict, Any

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QDialog, QGroupBox, QHBoxLayout

class DriverHistoryGui(QDialog):

    # Add a signal to check for data updating
    dataUpdated = Signal(object);
    
    def __init__(self, driver_id: int, driverName: str, driver_data_dict: Dict[int, Dict[str, Any]], parent=None):
        super().__init__(parent);
        self.driver_id = driver_id;
        self.driverName = driverName;
        self.driver_data_dict = driver_data_dict;
        self.setWindowTitle(f'Driver History: {driverName}');
        self.setMinimumSize(500, 450);
        # self.setGeometry(100, 100, 400, 600);
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint);
        bgColor = "rgba(19, 21, 22, 0.4)";
        self.setStyleSheet(f'background-color: {bgColor}');
    
        self.init_UI();
    
    def init_UI(self):
        # Make a VBox to display all the laps in 
        self.layout = QVBoxLayout(self);
        self.layout.setContentsMargins(10, 10, 10, 10);
        self.layout.setSpacing(10);

        self.scrollArea = QScrollArea();
        self.scrollArea.setWidgetResizable(True);
        self.contentWidget = QWidget();
        self.contentLayout = QVBoxLayout(self.contentWidget);
        self.contentLayout.setContentsMargins(10, 10, 10, 10);
        self.contentLayout.setSpacing(10);

        self.scrollArea.setWidget(self.contentWidget);
        self.layout.addWidget(self.scrollArea);
        self.setLayout(self.layout);
    
        self.update_UI(); # Update the UI
    
        self.dataUpdated.connect(self.updateDataSlot);
        
    def update_UI(self):

        for i in reversed(range(self.contentLayout.count())):
            widget = self.contentLayout.itemAt(i).widget();
            if widget is not None:
                widget.deleteLater();

        colour1 = "rgba(127, 127, 127, 0.4)";
        colour2 = "rgba(71, 71, 71, 0.4)";
        
        if self.driver_data_dict is None or self.driver_data_dict == {}:
            return;
    
        for index, lap_number in enumerate(sorted(self.driver_data_dict.keys(), reverse=True)):
            lapData = self.driver_data_dict[lap_number];

            group_box = QGroupBox();
            group_box.setStyleSheet(f'background-color: {colour1 if index % 2 == 0 else colour2}; padding: 10px;');
            group_layout = QVBoxLayout(group_box);
            group_layout.setContentsMargins(5, 5, 5, 5);
            group_layout.setSpacing(5);

            lapNumberLabel = QLabel(f'Lap: {lap_number}');
            lapNumberLabel.setAlignment(Qt.AlignCenter);

            positionLabel = QLabel(f'Position: {lapData['carPosition']}');
            positionLabel.setAlignment(Qt.AlignCenter);

            laptimeLabel = QLabel(f'Lap Time: {lapData['last_lapTime']}');
            laptimeLabel.setAlignment(Qt.AlignCenter);

            sector_layout = QHBoxLayout();
            sector_layout.setSpacing(5);
            
            sector1Label = QLabel(f'Sector 1: {lapData['time_sector1']}');
            sector1Label.setAlignment(Qt.AlignCenter);
            sector_layout.addWidget(sector1Label);

            sector2Label = QLabel(f'Sector 2: {lapData['time_sector2']}');
            sector2Label.setAlignment(Qt.AlignCenter);
            sector_layout.addWidget(sector2Label);

            sector3Label = QLabel(f'Sector 3: {lapData['time_sector3']}');
            sector3Label.setAlignment(Qt.AlignCenter);
            sector_layout.addWidget(sector3Label);

            group_layout.addWidget(lapNumberLabel);
            group_layout.addWidget(positionLabel);
            group_layout.addWidget(laptimeLabel);
            group_layout.addLayout(sector_layout);

            self.contentLayout.addWidget(group_box);

            # Add a separator to separate the entries
            separator = QFrame();
            separator.setFrameShape(QFrame.HLine);
            separator.setFrameShadow(QFrame.Sunken);
            self.contentLayout.addWidget(separator);

    @Slot(object)
    def updateDataSlot(self, new_driver_data_dict: Dict[int, Dict[str, Any]]):
        
        if isinstance(new_driver_data_dict, dict):
            self.driver_data_dict = new_driver_data_dict;
            self.update_UI();