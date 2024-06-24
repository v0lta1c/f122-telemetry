import threading
import json
import os

from packets import ParticipantData, LapTimeData
from constants import POSITION_SAVE_INTERVAL

class LogDrivers:

    def __init__(self, participant_data, laptime_data):
        self.participant_data: ParticipantData = participant_data;
        self.laptime_data: LapTimeData = laptime_data;
        self.position_timer = None;

    def start_position_timer(self):
        self.position_timer = threading.Timer(POSITION_SAVE_INTERVAL, self.save_current_positions);
        self.position_timer.start();

    def save_current_positions(self):
        driver_data = [];
        for key in self.participant_data.get_participant_data_list():
            driver_name = self.participant_data.get_participant(key)['m_name'];
            driver_position = self.laptime_data.get_lapdata_value_from_key(key)['m_carPosition'];
            driver_data.append({driver_name: driver_position});

        directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
        os.makedirs(directory, exist_ok=True);

        file_name = os.path.join(directory, "driverPositions.json");

        with open(file_name, 'w') as file:
            json.dump(driver_data, file, indent=4, separators=(',', ':'), ensure_ascii=False);

        self.start_position_timer();

    def stop_position_timer(self):
        if self.position_timer:
            self.position_timer.cancel();