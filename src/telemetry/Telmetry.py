import socket
import threading
import time
import select
import struct
from typing import List, Dict, Any, Callable

from constants import *
from packets import *
from DiscordIPCSocket import DiscordIPCSocket

from telemetry.PrintRaceData import RaceDataPrinter
from telemetry.LogDrivers import LogDrivers
from telemetry.PitStatus import PitStatusChecker

class Telemetry:
    def __init__(self, real_time_callback: Callable):
        self.running = False;
        self.discord_enabled = False; # Variable that checks the discord integration
        self.discord_ipc_socket = DiscordIPCSocket();
    
        # Initialize all the packets 
        self.participant_data = ParticipantData();
        self.participant_data_cache = ParticipantData();
        self.finalClassification_data = FinalClassification();
        self.session_data = SessionData();
        self.laptime_data = LapTimeData();
        self.car_damage_data = CarDamageData();
        self.car_telemetry_data = CarTelemetry();
        self.penalty_event = PenaltyEvent();
        self.car_status_data = CarStatusData();
        self.pit_status = PitStatusStorage();
        self.current_positions = CurrentDriverPositions();

        self.stop_event = threading.Event();
        self.real_time_callback = real_time_callback;
        self.update_timer = None;

        self.results_printed = 1; # Prevents double printing of the final output on console
        # Variables to track how many cars are still present in the session
        self.total_num_cars = 0;
        self.current_num_cars = 0;
        self.client = None;
    
        # Initialize the log drivers instance
        self.log_drivers = LogDrivers(self.participant_data, self.laptime_data, self.current_positions);
    
        # Initialize the pit status storage instance
        self.pit_status_storage = PitStatusChecker(self.laptime_data, self.pit_status, self.participant_data, self.car_status_data, self.send_ipc_trigger);
        self.pit_status_storage.in_session = False; # Flag to check whether the socket is actually listening to the data

    def start(self, discord_enabled):
        self.running = True;
        if discord_enabled:
            self.discord_enabled = True;
        
        self.thread = threading.Thread(target=self.socket_listener, name="Telemetry", daemon=True);
        self.thread.start();

        #Start the pit status thread here
        self.pit_status_thread = threading.Thread(target=self.pit_status_storage.check_pit_status, args=(self.discord_enabled,), name="Pit Status Checker", daemon=True);
        self.pit_status_thread.start();

    
        # Start the thread of the discord ipc socket
        if self.discord_enabled:
            self.discord_ipc_socket.start_ipc_socket_thread();
    
        # Start the update timer
        self.schedule_update();
        self.log_drivers.start_position_timer();

    def stop(self):
        self.running = False;
        self.stop_event.set();
        self.pit_status_storage.stop();

        if self.discord_enabled:
            self.discord_ipc_socket.join_ipc_socket_thread();

        if self.thread.is_alive():
            self.thread.join();
        
        if self.client is not None:
            self.client.close();
    
        # Stop the logging timer as well
        if self.log_drivers.position_timer is not None:
            self.log_drivers.stop_position_timer();
    
        if self.pit_status_thread.is_alive():
            self.pit_status_thread.join();
    
        # Stop the timer
        if hasattr(self, 'update_timer') and self.update_timer:
            self.update_timer.cancel()

    def socket_listener(self):

        if self.client is None:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
        self.client.bind((IP, UDP_PORT));
        print(f'Telemetry Client started on IP: {IP} and Port: {UDP_PORT}');

        position_timer = None;
        last_data_recv_time = time.time();

        while self.running and not self.stop_event.is_set():

            try:

                if self.stop_event.is_set(): return;
                ready = select.select([self.client], [], [], TIMEOUT);
                if ready[0]:

                    if self.client is None: return;

                    data, addr = self.client.recvfrom(1500); # open the client connection and recv data

                    last_data_recv_time = time.time();

                    self.pit_status_storage.in_session = True;

                    #   Separate the header
                    dataHeader = data[0:24]; #Header size: 24 bytes

                    (h_packetFormat, h_gameMajorVersion, h_gameMinorVersion, h_packetVersion, h_packetID, h_sessionUID, h_sessionTime, h_frameIdentifier, h_playerCarIndex, h_secondaryPlayerCarIndex) = struct.unpack(p_headerString, dataHeader);

                    match(h_packetID):

                        case 1: #Session Data Packet
                            inSession = True;
                            tempStr = [];
                            sessionData = [];
                            sessionData_marshals = [];
                            sessionData2 = [];
                            sessionData_weather = [];
                            sessionData3 = [];
                            sessionData = struct.unpack(p_sessionPacketString_1, data[24:43]);
                            sessionData = list(sessionData);
                            #Unpack all the marshal zones into a list
                            for i in range(21):
                                tempStr = struct.unpack(p_sessionPacketString_2, data[5*i+43:5*i+48]);
                                sessionData_marshals.append(tempStr);
                            sessionData.append(sessionData_marshals);

                            #Continue unpacking normally
                            sessionData2 = struct.unpack(p_sessionPacketString_3, data[148:151]);
                            sessionData2 = list(sessionData2);
                            sessionData.extend(sessionData2);

                            #Now unpack the WeatherForecastSamples
                            for i in range(56):
                                tempStr = struct.unpack(p_sessionPacketString_4, data[8*i+151:8*i+159]);
                                sessionData_weather.append(tempStr);
                            sessionData.append(sessionData_weather);
                        
                            #Now again unpack normally
                            sessionData3 = struct.unpack(p_sessionPacketString_5, data[599:632]);
                            sessionData3 = list(sessionData3);
                            sessionData.extend(sessionData3);

                            #Store it inside the Storage Class
                            self.session_data.add_session_data(sessionData);
                        
                        case 2: #Lap Data Packet
                            lapdataStr = [];
                            for i in range(22):
                                #Struct size : 43 bytes
                                lapdataStr = struct.unpack(p_lapDataPacketString, data[43*i+24:43*i+67]);
                                self.laptime_data.add_laptime_data(i, lapdataStr);

                        case 3: #Event Data Packet
                            eventDataStr = [];
                            eventType = struct.unpack(p_eventTypeString, data[24:28]);
                            eventType = ''.join(chr(num) for num in eventType);
                        
                            match eventType:

                                case EventStringCode.SESSION_STARTED.value:
                                    inSession = True;

                                case EventStringCode.FASTEST_LAP.value:
                                    e_fastestLapStr = struct.unpack('<Bf', data[28:33]);
                                    if self.discord_enabled and 'm_name' in self.participant_data.get_participant(e_fastestLapStr[0]):
                                        b, c = divmod(e_fastestLapStr[1]%3600, 60);
                                        driverName = self.participant_data.get_participant(e_fastestLapStr[0])['m_name'];
                                        self.send_ipc_trigger(f'FASTEST_LAP: Driver {driverName} has just set the fastest lap time of {int(b)}.{str(c)[:5]}');

                                case EventStringCode.PENALTY_ISSUED.value:
                                    penaltyStr = struct.unpack(p_eventPenaltyString, data[28:35]);
                                    self.penalty_event.add_penalty_data(penaltyStr);
                                    
                                    if 'm_name' in self.participant_data.get_participant(self.penalty_event.get_penalty_data_from_key('vehicleIdx')):
                                        penalisedDriver = self.participant_data.get_participant(self.penalty_event.get_penalty_data_from_key('vehicleIdx'))['m_name'];
                                        if self.discord_enabled:
                                            if self.penalty_event.get_penalty_data_from_key('penaltyType') == PenaltyTypes.DRIVE_THROUGH.value:
                                                self.send_ipc_trigger(f'DRIVE_THROUGH: Driver {penalisedDriver} has been issued a drive through penalty.');
                                            if self.penalty_event.get_penalty_data_from_key('penaltyType') == PenaltyTypes.TIME_PENALTY.value:
                                                self.send_ipc_trigger(f'TIME_PENALTY: Driver {penalisedDriver} has been issued a time penalty');
                        
                                case EventStringCode.RETIREMENT.value:
                                    e_retirementStr = data[28];
                                    if(self.discord_enabled) and 'm_name' in self.participant_data.get_participant(e_retirementStr):

                                        driverName = self.participant_data.get_participant(e_retirementStr)['m_name'];
                                        self.send_ipc_trigger(f'RETIREMENT: Driver {driverName} has retired from the session.');

                        case 4: #Participants Data Packet
                            numCars: int = data[24];
                            self.current_num_cars = numCars;
                            if self.current_num_cars >= self.total_num_cars:
                                self.total_num_cars = self.current_num_cars;
                            participantStr = [];
                            for i in range(numCars):
                                #Struct size: 14 bytes
                                participantStr = struct.unpack(p_participantsPacketString, data[56*i+25:56*i+39]);
                                self.participant_data.add_participant(i, participantStr);
                                #print(participant_data.get_participant_data_list().get(i).get('m_driverID'));

                            #This code block makes sure that the participant list stays updated throughout the whole race
                            #If participant data is smaller than the data in cache then replace the participant data with the cache
                            if len(self.participant_data.get_participant_data_list()) == numCars:
                                self.participant_data_cache.get_participant_data_list().update(self.participant_data.get_participant_data_list());
                        
                            if len(self.participant_data.get_participant_data_list()) != numCars and self.participant_data_cache.get_participant_data_list() is not None:
                                self.participant_data.get_participant_data_list().update(self.participant_data_cache.get_participant_data_list());


                        case 6: #Car Telemetry Packet
                            tempStr = [];
                            carTelemetryStr = [];

                            for i in range(22):
                                #Struct size: 60 bytes
                                tempStr = struct.unpack(p_carTelemetryPacketString_1, data[60*i+24:60*i+46]);
                                carTelemetryStr.extend(tempStr);
                                tempStr = struct.unpack(p_carTelemetryPacketString_2, data[60*i+46:60*i+54]);
                                carTelemetryStr.append(tempStr);
                                tempStr = struct.unpack(p_carTelemetryPacketString_3, data[60*i+54:60*i+58]);
                                carTelemetryStr.append(tempStr);
                                tempStr = struct.unpack(p_carTelemetryPacketString_4, data[60*i+58:60*i+62]);
                                carTelemetryStr.append(tempStr);
                                tempStr = struct.unpack(p_carTelemetryPacketString_5, data[60*i+62:60*i+64]);
                                carTelemetryStr.extend(tempStr);
                                tempStr = struct.unpack(p_carTelemetryPacketString_6, data[60*i+64:60*i+80]);
                                carTelemetryStr.append(tempStr);
                                tempStr = struct.unpack(p_carTelemetryPacketString_7, data[60*i+80:60*i+84]);
                                carTelemetryStr.append(tempStr);
                                self.car_telemetry_data.add_car_telemetry_data(i, carTelemetryStr);
                                carTelemetryStr.clear();

                        case 7: #Car Status Data Packet
                            carStatusData = [];
                            for i in range(22):
                                #Struct size: 47 bytes
                                carStatusData = struct.unpack(p_carStatusPacketString, data[47*i+24:47*i+71]);
                                self.car_status_data.update_car_status_data(i, carStatusData);

                        case 8: #Final  Classification Packet
                            numCars: int = data[24];
                            finalData = [];
                            for i in range(numCars):
                                #Struct size: 24 bytes
                                finalData = struct.unpack(p_finalClassificationPacketString, data[45*i+25:45*i+49]);
                                self.finalClassification_data.add_classification_data(i, finalData);

                            if(self.results_printed %2 == 0):
                                printer = RaceDataPrinter();
                                printer.print_data(numCars, self.finalClassification_data, self.participant_data, self.laptime_data, self.car_damage_data, self.session_data, self.current_positions);
                                inSession = False;
                                if position_timer is not None:
                                    position_timer.cancel();
                                if(self.discord_enabled):
                                    self.send_ipc_trigger('Race Data Trigger');
                            
                            if(self.results_printed == 1001):
                                self.results_printed = 1;
                            self.results_printed += 1;

                        case 10: #Car Damage Packet
                            tempStr = [];
                            carDamageStr = [];
                            
                            for i in range(22):
                                #Unpack all tyre wear into a list
                                tempStr = struct.unpack(p_carDamagePacketString_1, data[42*i+24:42*i+40]);
                                carDamageStr.append(list(tempStr));
                                #Unpack all tyre damage into a list
                                tempStr = struct.unpack(p_carDamagePacketString_2, data[42*i+40:42*i+44]);
                                carDamageStr.append(list(tempStr));
                                #unpack all brakes damage into a list
                                tempStr = struct.unpack(p_carDamagePacketString_3, data[42*i+44:42*i+48]);
                                carDamageStr.append(list(tempStr));
                                tempStr = struct.unpack(p_carDamagePacketString_4, data[42*i+48:42*i+66]);
                                carDamageStr.extend(tempStr);
                                self.car_damage_data.add_carDamage_Data(i, carDamageStr);
                                carDamageStr.clear();
                
                else:
                    # Socket did not receive any data for some time

                    # Set the in_session variable to false
                    self.pit_status_storage.in_session = False;
                    # This piece of code cancels the current driver position timer on timeout
                    current_time = time.time();
                    if current_time - last_data_recv_time >= TIMEOUT:
                        last_data_recv_time = current_time;
                        if position_timer is not None:
                            position_timer.cancel();
                            position_timer = None;
            
            except KeyboardInterrupt:
                break;

    def send_ipc_trigger(self, message: str):
        if self.discord_enabled:
            self.discord_ipc_socket.send_ipc_trigger(message);
    
    def schedule_update(self):
        if self.running: 
            if hasattr(self, 'update_timer') and self.update_timer:
                self.update_timer.cancel();
            
        self.update_timer = threading.Timer(5.0, self.update_real_time_summary);
        self.update_timer.start();
    
    def update_real_time_summary(self):
        if self.running:
            driver_dict = self.parse_real_time_summary();
            self.real_time_callback(driver_dict);
            self.schedule_update();

    def parse_real_time_summary(self) -> Dict[int, Dict[str, Any]]:

        # The data is processed and packed into a list.
        # List: [Participants: {Position, Name, Constructor, Interval, Best Lap, TyreCompound, Pitstops, Penalties}]

        # First store everything about a driver inside a list
        driver_list = [];

        for driver_id in range(self.total_num_cars):        

            if self.participant_data.get_participant(driver_id) is None: return;
            if self.car_status_data.get_car_status_data_from_key(driver_id) is None: return;
            if self.laptime_data.get_lapdata_value_from_key(driver_id) is None: return;
        
            position = self.laptime_data.get_lapdata_value_from_key(driver_id)['m_carPosition'];
            name = self.participant_data.get_participant(driver_id)['m_name'];
            constructor = TeamNames.get(TeamId(self.participant_data.get_participant(driver_id)['m_teamId']).value);
            interval = 0;
            best_lap = 0;
            tyre_compound = TyreCompoundNames.get(TyreCompound(self.car_status_data.get_car_status_data_from_key(driver_id)['m_visualTyreCompound']).value);
            pitstops = self.laptime_data.get_lapdata_value_from_key(driver_id)['m_numPitStops'];
            penalties = self.laptime_data.get_lapdata_value_from_key(driver_id)['m_penalties'];
        
            row = [position, name, constructor, interval, tyre_compound, pitstops, penalties];
            driver_list.append(row);

        # Sort the list based on the position
        driver_list.sort(key=lambda x: x[0]);

        # Convert the list into dictionary
        driver_dict = {i: {
            'Position': driver[0],
            'Name': driver[1],
            'Constructor': driver[2],
            'Interval': driver[3],
            'TyreCompound': driver[4],
            'Pitstops': driver[5],
            'Penalties': driver[6]
        } for i, driver in enumerate(driver_list)}

        return driver_dict 

    def calculate_interval(self, driver_id: int) -> str:

        interval = 0;
        #First get the position of the driver
        driver_position = self.laptime_data.get_lapdata_value_from_key(driver_id)['m_carPosition'];
        
        if driver_position == 1:
            interval = 0;
        else:
            for i in range(self.total_num_cars):
                if self.laptime_data.get_lapdata_value_from_key(i)['m_carPosition'] == driver_position-1:
                    car_ahead_interval = self.laptime_data.get_lapdata_value_from_key(i)['m_lastLapTimeInMS'];

    # Converts time (from ms) into a formatted string 
    # Output : Minutes:Seconds:Milliseconds
    def format_time_to_str(val: int) -> str:
        total_seconds = val / 1000;
        minutes, seconds = divmod(total_seconds, 60);

        seconds_in_int = int(seconds);
        ms = int((seconds-seconds_in_int) * 1000);
        return f"{int(minutes)}:{seconds_in_int:02d}:{ms:04d}";