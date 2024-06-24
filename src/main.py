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

if __name__ == '__main__':
    
    #Adds an argument "--enable_discord" which will enable the server to access the discord bot
    parser = argparse.ArgumentParser(description="Optional discord integration feature");
    parser.add_argument("--enable_discord", action="store_true", help="Enable discord messaging feature");
    args = parser.parse_args();

    if args.enable_discord:
        enableDiscordMessaging();

    # Start the gui thread here
    gui_thread = threading.Thread(target=gui.run_gui, args=(car_telemetry_data, participant_data, session_data), daemon=True);
    gui_thread.start();

    gui_thread.join();