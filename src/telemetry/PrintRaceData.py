import os
import json
import time
from typing import List, Dict
from constants import Track_Names, TrackId, Session_Type_Name, SessionType, createJSONFile, createStaticFileName
from shared import update_json_dump_file
from packets import ResultStatus, CurrentDriverPositions

class RaceDataPrinter:
    def __init__(self):
        self.create_JSON_file = createJSONFile;
        self.create_static_file_name = createStaticFileName;

    def print_data(self, numCars: int, final_classification_data, participant_data, laptime_data, car_damage_data, session_data, current_positions) -> None:
        #First we sort the array based on the car position
        sorted_fcData = sorted(final_classification_data.get_fcDict().items(), key=lambda item: item[1]['m_position']);
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
                    total_laps = current_positions.get_current_status_for_driver(key)['lap'];
                    print(f'Total laps: {val}');

            finalOutput.append([name, position, total_time, best_lap_time, penalties_time, total_laps, num_of_pitstops, result_status]);

            finalOutputCols = finalOutput[0];

            data = [];
            data.append([{"track_name": Track_Names.get(TrackId(session_data.get_session_data_from_key("m_trackId")).value)}, 
                        {"session_type": Session_Type_Name.get(SessionType(session_data.get_session_data_from_key("m_sessionType")).value)}]);
            for row in finalOutput[1:]:
                data.append({finalOutputCols[i]: value for i, value in enumerate(row)});

        update_json_dump_file(data);
        self.write_to_file(data);
        
    def write_to_file(self, data: List[Dict]) -> None:

        if(self.create_JSON_file):
            directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
            os.makedirs(directory, exist_ok=True)

            fileName = " ";
            fName = "telemetryData";
            fileExtension = ".json";
            timestr = time.strftime("%Y%m%d-%H%M%S");


            #Check whether name is static or dynamic
            if(self.create_static_file_name):
                fileName = "".join((fName, fileExtension));
            else:
                fileName = "".join((fName,timestr,fileExtension));
            
            fileName = os.path.join(directory, fileName);
            
            with open(fileName, 'w') as f:json.dump(data, f, indent=4, separators=(',', ': '), ensure_ascii=False);

