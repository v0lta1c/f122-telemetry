import threading
import time

from constants import TyreCompound
from packets import PitStatusStorage, LapTimeData, ParticipantData, CarStatusData
from server import update_event

"""
This function runs in a separate thread and checks the pit status of every vehicle.

By default, it calls out the driver and their fitted tyre with the correct age when they exit the pits.
Another option to call out the driver and their fitted tyre when they enter the pits is included but commented.

"""

class PitStatusChecker:
    def __init__(self, laptime_data, pit_status, participant_data, car_status_data):
        self.laptime_data: LapTimeData = laptime_data;
        self.pit_status: PitStatusStorage = pit_status;
        self.participant_data: ParticipantData = participant_data;
        self.car_status_data: CarStatusData = car_status_data;
        self.in_session = False;
        self.stop_event = threading.Event();

    def check_pit_status(self, discord_enabled):
        while not self.stop_event.is_set():
            if self.in_session and self.participant_data is not None:
                for driver in range(22):
                    if self.laptime_data.get_lapdata_value_from_key(driver) is None or self.car_status_data.get_car_status_data_from_key(driver) is None: continue;
                    current_pit_status = self.laptime_data.get_lapdata_value_from_key(driver)['m_pitStatus']

                    self.pit_status.update_pit_status(driver, current_pit_status)

                    if self.pit_status.on_status_change(driver):
                        driverDict = self.participant_data.get_participant_data_list()
                        if driver in driverDict:
                            driverName = self.participant_data.get_participant(driver)['m_name']
                            tyreAge = self.car_status_data.get_car_status_data_from_key(driver)['m_tyresAgeLaps']
                            tyreCompound = self.car_status_data.get_car_status_data_from_key(driver)['m_visualTyreCompound']
                            tyreCompoundName = TyreCompound(tyreCompound).name

                            ## Uncomment if you want to also call out when a driver enters the pits

                            #if current_pit_status == 1:
                            #    if tyreAge == 0:
                            #        send_ipc_trigger(f'PIT_CHANGE: Driver {driverName} is entering the pits with fresh {tyreCompoundName}s');
                            #    else:
                            #        send_ipc_trigger(f'PIT_CHANGE: Driver {driverName} is entering the pits with {tyreAge} laps old {tyreCompoundName}s.');
                            
                            if current_pit_status == 0 and discord_enabled:
                                if tyreAge == 0:

                                    pit_data = {
                                        'driver': driverName,
                                        'tyreCompound': tyreCompoundName
                                    }

                                    update_event('pit-change', pit_data);

                                else:
                                    
                                    pit_data = {
                                        'driver': driverName,
                                        'tyreAge': tyreAge,
                                        'tyreCompound': tyreCompoundName
                                    }

                                    update_event('pit-change', pit_data);

                time.sleep(10);

    def stop(self):
        self.stop_event.set();
