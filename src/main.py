from constants import *
from packets import *
import shared
from typing import Dict, Any, List
from server import run_server
from ui import gui
import threading
import socket
import select
import struct
import sys
import os
import json
import time
import argparse

#Hello im in the gui dev branch

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

    #Start the pit status thread here
    pit_status_thread = threading.Thread(target=check_pit_status);
    pit_status_thread.start();

    # Start the gui thread here
    gui_thread = threading.Thread(target=gui.run_gui, args=(car_telemetry_data, participant_data, session_data), daemon=True);
    gui_thread.start();

    #Run the main function
    main();

    server_thread.join();
    pit_status_thread.join();
    gui_thread.join();