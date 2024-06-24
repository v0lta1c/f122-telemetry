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

#   Utility variable for enabling the discord bot integration
discordMessagingEnabled = False;

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

#Function to change the value of the global variable discordMessagingEnabled

def enableDiscordMessaging() -> None:
    global discordMessagingEnabled;
    discordMessagingEnabled = True;

    return

"""
This function runs in a separate thread and checks the pit status of every vehicle.

By default, it calls out the driver and their fitted tyre with the correct age when they exit the pits.
Another option to call out the driver and their fitted tyre when they enter the pits is included but commented.

"""

def check_pit_status():
    while True:
        for driver in range(22):
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
                            pass;
                            #send_ipc_trigger(f'PIT_CHANGE: Driver {driverName} is leaving the pits with fresh {tyreCompoundName}s.');
                        else:
                            pass;
                            #send_ipc_trigger(f'PIT_CHANGE: Driver {driverName} is leaving the pits with {tyreAge} laps old {tyreCompoundName}s.');

        time.sleep(10);

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

    server_thread.join();
    pit_status_thread.join();
    gui_thread.join();