from typing import Dict, Any

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QGroupBox, QHBoxLayout

class CarHistoryGui(QDialog):

    # Add a signal for data updating
    dataUpdated = Signal(object);

    def __init__(self, driver_id: int, driverName: str, car_data_dict: Dict[int, Dict[str, Any]], parent=None):

        super().__init__(parent);
        self.driver_id = driver_id;
        self.driverName = driverName;
        self.car_data_dict = car_data_dict;
        self.setWindowTitle(f'Car History: {driverName}');
        self.setMinimumSize(500, 450);
        # self.setGeometry(100, 100, 400, 600);
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint);
        bgColor = "rgba(19, 21, 22, 0.4)";
        self.setStyleSheet(f'background-color: {bgColor}');

        self.init_UI();

    def init_UI(self):

        # Make a Vbox to display all the laps in

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

        if self.car_data_dict is None or self.car_data_dict == {}:
            return;
    
        for index, lap_number in enumerate(sorted(self.car_data_dict.keys(), reverse=True)):
            carData = self.car_data_dict[lap_number];

            group_box = QGroupBox();
            group_box.setStyleSheet(f'background-color: {colour1 if index % 2 == 0 else colour2}; padding: 10px;');
            group_layout = QVBoxLayout(group_box);
            group_layout.setContentsMargins(5, 5, 5, 5);
            group_layout.setSpacing(5);

            title_layout = QHBoxLayout();
            title_layout.setSpacing(5);

            lapNumberLabel = QLabel(f'Lap: {lap_number}');
            lapNumberLabel.setAlignment(Qt.AlignCenter);
            title_layout.addWidget(lapNumberLabel, alignment=Qt.AlignCenter);

            pitsLabel = QLabel(f'P');
            pitsLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter);
            pitsLabel.setVisible(carData['isInPits']);

            if carData["isInPits"]:
                title_layout.addStretch();  # Add stretch to push P to side
                title_layout.addWidget(pitsLabel, alignment=Qt.AlignRight);
            
            positionLabel = QLabel(f'Position: {carData['carPosition']}');
            positionLabel.setAlignment(Qt.AlignCenter);

            ersLabel = QLabel(f'Ers Used: {int(carData['ersHarvested'])}%');
            ersLabel.setAlignment(Qt.AlignCenter);

            tyreWearLabel = QLabel(f'Tyre Wear');
            tyreWearLabel.setAlignment(Qt.AlignCenter);

            tyreWearFront = QHBoxLayout();
            tyreWearFront.setSpacing(5);

            tyreFLLabel = QLabel(f'{carData['tyreFLWear']}');
            tyreFLLabel.setAlignment(Qt.AlignCenter);
            tyreWearFront.addWidget(tyreFLLabel);

            tyreFRLabel = QLabel(f'{carData['tyreFRWear']}');
            tyreFRLabel.setAlignment(Qt.AlignCenter); 
            tyreWearFront.addWidget(tyreFRLabel);

            tyreWearRear = QHBoxLayout();
            tyreWearRear.setSpacing(5);

            tyreRLLabel = QLabel(f'{carData['tyreRLWear']}');
            tyreRLLabel.setAlignment(Qt.AlignCenter);
            tyreWearRear.addWidget(tyreRLLabel);

            tyreRRLabel = QLabel(f'{carData['tyreRRWear']}');
            tyreRRLabel.setAlignment(Qt.AlignCenter); 
            tyreWearRear.addWidget(tyreRRLabel);

            group_layout.addLayout(title_layout);
            group_layout.addWidget(positionLabel);
            group_layout.addWidget(ersLabel);
            group_layout.addWidget(tyreWearLabel);
            group_layout.addLayout(tyreWearFront);
            group_layout.addLayout(tyreWearRear);

            self.contentLayout.addWidget(group_box);

            # Add a separator to separate the entries
            separator = QFrame();
            separator.setFrameShape(QFrame.HLine);
            separator.setFrameShadow(QFrame.Sunken);
            self.contentLayout.addWidget(separator);

    @Slot(object)
    def updateDataSlot(self, new_car_data_dict: Dict[int, Dict[str, Any]]):
        
        if isinstance(new_car_data_dict, dict):
            self.car_data_dict = new_car_data_dict;
            self.update_UI();

    

