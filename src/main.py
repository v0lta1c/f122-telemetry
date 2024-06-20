from constants import *
from packets import *
import shared
from typing import Dict, Any, List
from server import run_server
#from app_gui import run_gui
import threading
import socket
import select
import struct
import sys
import os
import json
import time
import argparse

#Other vars
"""
TODO List

2. Add another API endpoint for continuous streaming data

"""

""" Var to check whether the results have been printed or not
    Prevents duplicating of results on the print page"""

listeningSocketActive = False;

resultsPrinted: int = 1;

#   Utility variable for pit_status, helps check whether the session is ongoing or not
inSession: int = False;

#   Utility variable for enabling the discord bot integration
discordMessagingEnabled = False;

# Timer to check the driver positions
position_timer = None;

#Storage variables for the packetData

participant_data = ParticipantData();
participant_data_cache = ParticipantData();
finalClassification_data = FinalClassification();
session_data = SessionData();
laptime_data = LapTimeData();
car_damage_data = CarDamageData();
car_telemetry_data = CarTelemetry();
penalty_event = PenaltyEvent();
car_status_data = CarStatusData();
pit_status = PitStatusStorage();
current_positions = CurrentDriverPositions();

"""
This function runs in its seprate thread and is responsible for the socket that sends data to the discord bot. 
Necessary if --enable_discord was set.
"""

ipc_socket = None;

def connect_to_ipc():
    if discordMessagingEnabled:
        global ipc_socket;
        while True:    
            try:
                ipc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM); 
                ipc_socket.connect((IP_discordIPC, PORT_discordIPC));
                print("Connected to the IPC Socket");
                
                #keepAlive
                while True:
                    time.sleep(1);

            except ConnectionRefusedError:
                print("Failed to connect to IPC: Connection Refused.\nRetrying in 5 seconds.....");
                time.sleep(5);

            except Exception as e:
                print(f'Error occured: {e}');
                time.sleep(5);

#Function to change the value of the global variable discordMessagingEnabled

def enableDiscordMessaging() -> None:
    global discordMessagingEnabled;
    discordMessagingEnabled = True;

    return

def printData(numCars: int) -> None:

    #   Sort the final classification dictionary

    #First we sort the array based on the car position
    sorted_fcData = sorted(finalClassification_data.get_fcDict().items(), key=lambda item: item[1]['m_position']);
    #slice the array based on the number of cars
    sliced_sorted_fcData = sorted_fcData[:numCars];
    #finally convert it into a dict
    fcDataSorted = dict(sliced_sorted_fcData);

    #Sort the participant data and car damage data based on the keys of final classification packet
    print(f'Participant Data Dict: {participant_data.get_participant_data_list()}');
    print(f'fcDataSorted Dict: {fcDataSorted}');
    print(f'Numcars: {numCars}');
    partDataSorted = {key: participant_data.get_participant_data_list()[key] for key in fcDataSorted};
    carDamageDataSorted = {key: car_damage_data.get_carDamage_dict()[key] for key in fcDataSorted};
    laptimeDataSorted = {key: laptime_data.get_lapdata_dict()[key] for key in fcDataSorted};

    #   Make a List for the final output string
    finalOutput = []
    finalOutput.append(["name", "position", "total_time", "best_lap_time", "penalties_time", "total_laps", "num_of_pitstops", "result_status"]);
    name: str;
    position: int;
    total_time: int;
    best_lap_time: int;
    penalties_time: int;
    total_laps: int;
    num_of_pitstops: int;
    result_status: str;
    index: int = 0;

    print(f'Track : {Track_Names.get(TrackId(session_data.get_session_data_from_key("m_trackId")).value)}\n');
    print(f'Session Type: {Session_Type_Name.get(SessionType(session_data.get_session_data_from_key("m_sessionType")).value)}\n');

    for key in fcDataSorted.keys():
        fcVal = fcDataSorted[key];
        pdVal = partDataSorted[key];
        cdVal = carDamageDataSorted[key];
        lpVal = laptimeDataSorted[key];
        if(index<=numCars):
            index += 1;
        else:
            break;
        
        for inner_key, val in pdVal.items():
            if(inner_key == 'm_name'):
                print(f'\nName: {val}');
                name = val;
        for inner_key, val in fcVal.items():
            if(inner_key == 'm_position'):
                print(f'Position: {val}');
                position = val;
            if(inner_key == 'm_totalRaceTime'):
                b, c = divmod(val%3600, 60);
                print(f'Total Time: {int(b)}:{c}');
                total_time = val*1000000;
            if(inner_key == 'm_bestLapTimeInMS'):
                b, c = divmod((val/1000)%3600, 60);
                print(f'Best Lap Time: {int(b)}:{c}');
                best_lap_time = val*1000;
            if(inner_key == 'm_penaltiesTime'):
                b, c = divmod(val%3600, 60);
                print(f'Total Penalties Time: {int(b)}:{c}');
                penalties_time = val;
            if(inner_key == 'm_numPitStops'):
                print(f'Total Pitstops: {val}');
                num_of_pitstops = val;
            if(inner_key == 'm_resultStatus'):
                print(f'Status: {ResultStatus(val).name}');
                result_status = ResultStatus(val).name;
        for inner_key, val in cdVal.items():
            if(inner_key == 'm_gearBoxDamage'):
                print(f'GearBox Damage: {val}%');
            if(inner_key == 'm_tyresWear'):
                print(f'Tyre Wear: {val}');
        for inner_key, val in lpVal.items():
            if(inner_key == 'm_currentLapNum'):
                total_laps = val;
                print(f'Total laps: {val}');

        finalOutput.append([name, position, total_time, best_lap_time, penalties_time, total_laps, num_of_pitstops, result_status]);

        finalOutputCols = finalOutput[0];

        data = [];
        data.append([{"track_name": Track_Names.get(TrackId(session_data.get_session_data_from_key("m_trackId")).value)}, 
                    {"session_type": Session_Type_Name.get(SessionType(session_data.get_session_data_from_key("m_sessionType")).value)}]);
        for row in finalOutput[1:]:
            data.append({finalOutputCols[i]: value for i, value in enumerate(row)});

    shared.update_json_dump_file(data);
    writeToFile(data);

"""
This function runs in a separate thread and checks the pit status of every vehicle.

By default, it calls out the driver and their fitted tyre with the correct age when they exit the pits.
Another option to call out the driver and their fitted tyre when they enter the pits is included but commented.

"""

def check_pit_status():
    while True:
        for driver in range(22):
            if inSession:
                current_pit_status = laptime_data.get_lapdata_value_from_key(driver)['m_pitStatus'];

                pit_status.update_pit_status(driver, current_pit_status);

                if pit_status.on_status_change(driver):
                    driverDict = participant_data.get_participant_data_list();
                    if driver in driverDict:
                        driverName = participant_data.get_participant(driver)['m_name'];
                        tyreAge = car_status_data.get_car_status_data_from_key(driver)['m_tyresAgeLaps'];
                        tyreCompound = car_status_data.get_car_status_data_from_key(driver)['m_visualTyreCompound'];
                        tyreCompoundName = TyreCompound(tyreCompound).name;

                        ## Uncomment if you want to also call out when a driver enters the pits

                        #if current_pit_status == 1:
                        #    if tyreAge == 0:
                        #        send_ipc_trigger(f'PIT_CHANGE: Driver {driverName} is entering the pits with fresh {tyreCompoundName}s');
                        #    else:
                        #        send_ipc_trigger(f'PIT_CHANGE: Driver {driverName} is entering the pits with {tyreAge} laps old {tyreCompoundName}s.');
                        
                        if current_pit_status == 0 and discordMessagingEnabled:
                            if tyreAge == 0:
                                send_ipc_trigger(f'PIT_CHANGE: Driver {driverName} is leaving the pits with fresh {tyreCompoundName}s.');
                            else:
                                send_ipc_trigger(f'PIT_CHANGE: Driver {driverName} is leaving the pits with {tyreAge} laps old {tyreCompoundName}s.');

        time.sleep(10);

def send_ipc_trigger(message: str) -> None:

    if discordMessagingEnabled:
        global ipc_socket;
        if ipc_socket is None:
            print("No IPC connection available");

        try:
            ipc_socket.sendall(message.encode());
        except Exception as e:
            print(f'Error: Failed to send data over IPC: {e}');

def writeToFile(data: List[Dict]) -> None:

    if(createJSONFile):
        directory = "logs";
        os.makedirs(directory, exist_ok = True);

        fileName = " ";
        fName = "logs/telemetryData";
        fileExtension = ".json";
        timestr = time.strftime("%Y%m%d-%H%M%S");


        #Check whether name is static or dynamic
        if(createStaticFileName):
            fileName = "".join((fName, fileExtension));
        else:
            fileName = "".join((fName,timestr,fileExtension));
        
        with open(fileName, 'w') as f:json.dump(data, f, indent=4, separators=(',', ': '), ensure_ascii=False);    

""" 
    The following function save_current_positions records the positions of drivers every 30 seconds and writes it to a file.
    This is to account for backup purposes if and when the multiplayer session bugs out.    

"""

def start_position_timer() -> None:
    global position_timer;

    # We use the timer sub-class from thread and make a new object every 30 seconds
    position_timer = threading.Timer(POSITION_SAVE_INTERVAL, save_current_positions);
    position_timer.start();

def save_current_positions() -> None:

    global position_timer;

    driverName: str;
    driverPosition: int;
    data = [];
    for key in participant_data.get_participant_data_list():
        driverName = participant_data.get_participant(key)['m_name'];
        driverPosition = laptime_data.get_lapdata_value_from_key(key)['m_carPosition'];
        data.append({driverName: driverPosition});

    # Save the driver positions to a file
    directory = "logs";
    os.makedirs(directory, exist_ok=True);

    fileName = "";
    fName = "logs/driverPositions";
    fileExtension = ".json";
    fileName = "".join((fName, fileExtension));
    with open(fileName, 'w') as f:json.dump(data, f, indent=4, separators=(',', ':'), ensure_ascii=False);

    # Call the timer again and restart the process
    start_position_timer();

def main() -> None:

    global resultsPrinted;
    global inSession;
    global listeningSocketActive;
    global position_timer;
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
    client.bind((IP, UDP_PORT));
    print(f'Telemetry Client started on IP: {IP} and Port: {UDP_PORT}');

    position_timer = None;

    last_data_recv_time = time.time();
    while(True):

        try:

            ready = select.select([client], [], [], TIMEOUT);
            if ready[0]:
                data, addr = client.recvfrom(1500); # open the client connection and recv data

                last_data_recv_time = time.time();

                if(listeningSocketActive == False):
                    start_position_timer();
                
                listeningSocketActive = True;
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
                        session_data.add_session_data(sessionData);
                    
                    case 2: #Lap Data Packet
                        lapdataStr = [];
                        for i in range(22):
                            #Struct size : 43 bytes
                            lapdataStr = struct.unpack(p_lapDataPacketString, data[43*i+24:43*i+67]);
                            laptime_data.add_laptime_data(i, lapdataStr);

                    case 3: #Event Data Packet
                        eventDataStr = [];
                        eventType = struct.unpack(p_eventTypeString, data[24:28]);
                        eventType = ''.join(chr(num) for num in eventType);
                    
                        match eventType:

                            case EventStringCode.SESSION_STARTED.value:
                                inSession = True;

                            case EventStringCode.FASTEST_LAP.value:
                                e_fastestLapStr = struct.unpack('<Bf', data[28:33]);
                                if discordMessagingEnabled and 'm_name' in participant_data.get_participant(e_fastestLapStr[0]):
                                    b, c = divmod(e_fastestLapStr[1]%3600, 60);
                                    driverName = participant_data.get_participant(e_fastestLapStr[0])['m_name'];
                                    send_ipc_trigger(f'FASTEST_LAP: Driver {driverName} has just set the fastest lap time of {int(b)}.{str(c)[:5]}');

                            case EventStringCode.PENALTY_ISSUED.value:
                                penaltyStr = struct.unpack(p_eventPenaltyString, data[28:35]);
                                penalty_event.add_penalty_data(penaltyStr);
                                
                                if 'm_name' in participant_data.get_participant(penalty_event.get_penalty_data_from_key('vehicleIdx')):
                                    penalisedDriver = participant_data.get_participant(penalty_event.get_penalty_data_from_key('vehicleIdx'))['m_name'];
                                    if discordMessagingEnabled:
                                        if penalty_event.get_penalty_data_from_key('penaltyType') == PenaltyTypes.DRIVE_THROUGH.value:
                                            send_ipc_trigger(f'DRIVE_THROUGH: Driver {penalisedDriver} has been issued a drive through penalty.');
                                        if penalty_event.get_penalty_data_from_key('penaltyType') == PenaltyTypes.TIME_PENALTY.value:
                                            send_ipc_trigger(f'TIME_PENALTY: Driver {penalisedDriver} has been issued a time penalty');
                    
                            case EventStringCode.RETIREMENT.value:
                                e_retirementStr = data[28];
                                if(discordMessagingEnabled) and 'm_name' in participant_data.get_participant(e_retirementStr):

                                    driverName = participant_data.get_participant(e_retirementStr)['m_name'];
                                    send_ipc_trigger(f'RETIREMENT: Driver {driverName} has retired from the session.');

                    case 4: #Participants Data Packet
                        numCars: int = data[24];
                        participantStr = [];
                        for i in range(numCars):
                            #Struct size: 14 bytes
                            participantStr = struct.unpack(p_participantsPacketString, data[56*i+25:56*i+39]);
                            participant_data.add_participant(i, participantStr);
                            #print(participant_data.get_participant_data_list().get(i).get('m_driverID'));

                        #This code block makes sure that the participant list stays updated throughout the whole race
                        #If participant data is smaller than the data in cache then replace the participant data with the cache
                        if len(participant_data.get_participant_data_list()) == numCars:
                            participant_data_cache.get_participant_data_list().update(participant_data.get_participant_data_list());
                    
                        if len(participant_data.get_participant_data_list()) != numCars and participant_data_cache.get_participant_data_list() is not None:
                            participant_data.get_participant_data_list().update(participant_data_cache.get_participant_data_list());


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
                            car_telemetry_data.add_car_telemetry_data(i, carTelemetryStr);
                            carTelemetryStr.clear();

                    case 7: #Car Status Data Packet
                        carStatusData = [];
                        for i in range(22):
                            #Struct size: 47 bytes
                            carStatusData = struct.unpack(p_carStatusPacketString, data[47*i+24:47*i+71]);
                            car_status_data.update_car_status_data(i, carStatusData);

                    case 8: #Final  Classification Packet
                        numCars: int = data[24];
                        finalData = [];
                        for i in range(numCars):
                            #Struct size: 24 bytes
                            finalData = struct.unpack(p_finalClassificationPacketString, data[45*i+25:45*i+49]);
                            finalClassification_data.add_classification_data(i, finalData);

                        if(resultsPrinted %2 == 0):
                            printData(numCars);
                            inSession = False;
                            position_timer.cancel();
                            if(discordMessagingEnabled):
                                send_ipc_trigger('Race Data Trigger');
                        
                        if(resultsPrinted == 1001):
                            resultsPrinted = 1;
                        resultsPrinted += 1;

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
                            car_damage_data.add_carDamage_Data(i, carDamageStr);
                            carDamageStr.clear();
            else:

                # Socket did not receive any data for some time

                # This piece of code cancels the current driver position timer on timeout
                current_time = time.time();
                if current_time - last_data_recv_time >= TIMEOUT:
                    listeningSocketActive = False;
                    last_data_recv_time = current_time;
                    if position_timer is not None:
                        position_timer.cancel();
                        position_timer = None;
        except KeyboardInterrupt:
            sys.exit(0);

if __name__ == '__main__':
    
    #Adds an argument "--enable_discord" which will enable the server to access the discord bot
    parser = argparse.ArgumentParser(description="Optional discord integration feature");
    parser.add_argument("--enable_discord", action="store_true", help="Enable discord messaging feature");
    args = parser.parse_args();

    if args.enable_discord:
        enableDiscordMessaging();

    #Start the server in a separate thread
    server_thread = threading.Thread(target=run_server);
    server_thread.start();

    #Start the discord socket here
    socket_thread = threading.Thread(target=connect_to_ipc);
    socket_thread.start();

    #Start the pit status thread here
    pit_status_thread = threading.Thread(target=check_pit_status);
    pit_status_thread.start();

    #Start the gui thread here
    #gui_thread = threading.Thread(target=run_gui, args=(car_telemetry_data, participant_data, session_data), daemon=True);
    #gui_thread.start();

    #Run the main function
    main();

    server_thread.join();
    socket_thread.join();
    pit_status_thread.join();
    #gui_thread.join();