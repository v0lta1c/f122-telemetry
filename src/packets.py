"""TODO: Add the data storage mechanism for the packets"""

from typing import Dict, Any, List
from ctypes import c_uint8, c_char
from enum import Enum
import time

def decodeString(encodedString):
	decodedString = encodedString.decode('latin-1');
	return decodedString;

#   Storage class for Participant Data Packet
class ParticipantData:
    def __init__(self):
        self.data: Dict[int, Dict[str, Any]] = {};

    def add_participant(self, key: int, participant_data: List[Any]):

        m_aiControlled = participant_data[0];
        m_driverID = participant_data[1];
        m_networkID = participant_data[2];
        m_teamID = participant_data[3];
        m_myTeam = participant_data[4];
        m_raceNumber = participant_data[5];
        m_nationality = participant_data[6];
        m_name = participant_data[7];
        m_yourTelemetry = participant_data[8];


        self.data[key] = {
            'm_aiControlled' : m_aiControlled,
            'm_driverID' : m_driverID,
            'm_networkID' : m_networkID,
            'm_teamID' : m_teamID,
            'm_myTeam' : m_myTeam,
            'm_raceNumber' : m_raceNumber,
            'm_nationality' : m_nationality,
            'm_name' : m_name.decode('utf-8').rstrip('\x00'),
            'm_yourTelemetry' : m_yourTelemetry
        }

    def get_participant(self, key: int) -> Dict[str, Any]:
        return self.data.get(key, {})
    
    def __repr__(self):
        return repr(self.data);

    def get_participant_data_list(self) -> Dict[int, Dict[str, Any]]:
        return self.data;

#   Storage class for Final Classification Packet
class FinalClassification:
    def __init__(self):
        self.data: Dict[int, Dict[str, Any]] = {};

    def add_classification_data(self, key: int, final_classification: List[Any]):
         
        m_position = final_classification[0];
        m_numLaps = final_classification[1];
        m_gridPosition = final_classification[2];
        m_points = final_classification[3];
        m_numPitStops = final_classification[4];
        m_resultStatus = final_classification[5];
        m_bestLapTimeInMS = final_classification[6];
        m_totalRaceTime = final_classification[7];
        m_penaltiesTime = final_classification[8];
        m_numPenalties = final_classification[9];
        m_numTyreStints = final_classification[10];
        m_tyreStintsActual = final_classification[11];
        m_tyreStintsVisual = final_classification[12];
        m_tyreStintsEndlaps = final_classification[13];

        self.data[key] = {

            'm_position' : m_position,
            'm_numLaps' : m_numLaps,
            'm_gridPosition' : m_gridPosition,
            'm_points' : m_points,
            'm_numPitStops' : m_numPitStops,
            'm_resultStatus' : m_resultStatus,
            'm_bestLapTimeInMS' : m_bestLapTimeInMS,
            'm_totalRaceTime' : m_totalRaceTime,
            'm_penaltiesTime' : m_penaltiesTime,
            'm_numPenalties' : m_numPenalties,
            'm_numTyreStints' : m_numTyreStints,
            'm_tyreStintsActual' : m_tyreStintsActual,
            'm_tyreStintsVisual' : m_tyreStintsVisual,
            'm_tyreStintsEndlaps' : m_tyreStintsEndlaps
        }
    
    def get_fcEntry(self, key: int) -> Dict[str, Any]:
        return self.data.get(key);

    def __repr__(self):
        return repr(self.data);

    def get_fcDict(self) -> Dict[int, Dict[str, Any]]:
        return self.data;

"""Extra data types for the final classification packet"""

class ResultStatus(Enum):
    Invalid = 0;
    Inactive = 1;
    Active = 2;
    Finished = 3;
    DNF = 4;
    DSQ = 5;
    NOT_CLASSIFIED = 6;
    Retired = 7;

#   Storage Class for the Session Data Packet
class SessionData:
    def __init__(self):
        self.data: Dict[str, Any] = {};

    def add_session_data(self, sessionPacketData) -> None:

        self.data = {
            'm_weather' : sessionPacketData[0],
            'm_trackTemperature' : sessionPacketData[1],
            'm_airTemperature' : sessionPacketData[2],
            'm_totalLaps' : sessionPacketData[3],
            'm_trackLength' : sessionPacketData[4],
            'm_sessionType' : sessionPacketData[5],
            'm_trackId' : sessionPacketData[6],
            'm_formula' : sessionPacketData[7],
            'm_sessionTimeLeft' : sessionPacketData[8],
            'm_sessionDuration' : sessionPacketData[9],
            'm_pitSpeedLimit' : sessionPacketData[10],
            'm_gamePaused' : sessionPacketData[11],
            'm_isSpectating' : sessionPacketData[12],
            'm_spectatorCarIndex' : sessionPacketData[13],
            'm_sliProNativeSupport' : sessionPacketData[14],
            'm_numMarshalZones' : sessionPacketData[15],
            'm_marshalZones' : sessionPacketData[16],
            'm_safetyCarStatus' : sessionPacketData[17],
            'm_networkGame' : sessionPacketData[18],
            'm_numWeatherForecaseSamples' : sessionPacketData[19],
            'm_weatherForecastSamples' : sessionPacketData[20],
            'm_forecastAccuracy' : sessionPacketData[21],
            'm_aiDifficulty' : sessionPacketData[22],
            'm_seasonLinkIdentifier' : sessionPacketData[23],
            'm_weekendLinkIdentifier' : sessionPacketData[24],
            'm_sessionLinkIdentifier' : sessionPacketData[25],
            'm_pitstopWindowIdealLap' : sessionPacketData[26],
            'm_pitstopWindowLatestLap' : sessionPacketData[27],
            'm_pitstopRejoinPosition' : sessionPacketData[28],
            'm_steeringAssist' : sessionPacketData[29],
            'm_brakingAssist' : sessionPacketData[30],
            'm_gearboxAssist' : sessionPacketData[31],
            'm_pitAssist' : sessionPacketData[32],
            'm_pitReleaseAssist' : sessionPacketData[33],
            'm_ERSAssist' : sessionPacketData[34],
            'm_DRSAssist' : sessionPacketData[35],
            'm_dynamicRacingLine' : sessionPacketData[36],
            'm_dynamicRacingLineType' : sessionPacketData[37],
            'm_gameMode' : sessionPacketData[38],
            'm_ruleset' : sessionPacketData[39],
            'm_timeOfDay' : sessionPacketData[40],
            'm_sessionLength' : sessionPacketData[41]
        }

    def get_session_data_from_key(self, key) -> Any:
        return self.data.get(key)
    
    def __repr__(self):
        return repr(self.data)

    def get_session_data_dict(self) -> Dict[str, Any]:
        return self.data
    
#   Storage Class for LapTime Data Packet
class LapTimeData:
    def __init__(self):
        self.data: Dict[int, Dict[str, Any]] = {};

    def add_laptime_data(self, key: int, lapTimeDataString: List[Any]) -> None:

        m_lastLapTimeInMS =  lapTimeDataString[0];
        m_currentLapTimeInMS = lapTimeDataString[1];
        m_sector1TimeInMS = lapTimeDataString[2];
        m_sector2TimeInMS = lapTimeDataString[3];
        m_lapDistance = lapTimeDataString[4];
        m_totalDistance = lapTimeDataString[5];
        m_safetyCarDelta = lapTimeDataString[6];
        m_carPosition = lapTimeDataString[7];
        m_currentLapNum = lapTimeDataString[8];
        m_pitStatus = lapTimeDataString[9];
        m_numPitStops = lapTimeDataString[10];
        m_sector = lapTimeDataString[11];
        m_currentLapInvalid = lapTimeDataString[12];
        m_penalties = lapTimeDataString[13];
        m_warnings = lapTimeDataString[14];
        m_numUnservedDriveThroughPens = lapTimeDataString[15];
        m_numUnservedStopGoPens = lapTimeDataString[16];
        m_gridPosition = lapTimeDataString[17];
        m_driverStatus = lapTimeDataString[18];
        m_resultStatus = lapTimeDataString[19];
        m_pitLaneTimerActive = lapTimeDataString[20];
        m_pitLaneTimeInLaneInMS= lapTimeDataString[21];
        m_pitStopTimerInMS = lapTimeDataString[22];
        m_pitStopShouldServePen = lapTimeDataString[23];

        self.data[key] = {
            'm_lastLapTimeInMS': m_lastLapTimeInMS,
            'm_currentLapTimeInMS': m_currentLapTimeInMS,
            'm_sector1TimeInMS': m_sector1TimeInMS,
            'm_sector2TimeInMS': m_sector2TimeInMS,
            'm_lapDistance': m_lapDistance,
            'm_totalDistance': m_totalDistance,
            'm_safetyCarDelta': m_safetyCarDelta,
            'm_carPosition': m_carPosition,
            'm_currentLapNum': m_currentLapNum,
            'm_pitStatus': m_pitStatus,
            'm_numPitStops': m_numPitStops,
            'm_sector': m_sector,
            'm_currentLapInvalid': m_currentLapInvalid,
            'm_penalties': m_penalties,
            'm_warnings': m_warnings,
            'm_numUnservedDriveThroughPens': m_numUnservedDriveThroughPens,
            'm_numUnservedStopGoPens': m_numUnservedStopGoPens,
            'm_gridPosition': m_gridPosition,
            'm_driverStatus': m_driverStatus,
            'm_resultStatus': m_resultStatus,
            'm_pitLaneTimerActive': m_pitLaneTimerActive,
            'm_pitLaneTimeInLaneInMS': m_pitLaneTimeInLaneInMS,
            'm_pitStopTimerInMS': m_pitStopTimerInMS,
            'm_pitStopShouldServePen': m_pitStopShouldServePen,
        };

    def get_lapdata_value_from_key(self, key: int) -> Dict[str, Any]:
        return self.data.get(key)
    
    def get_lapdata_dict(self) -> Dict[int, Dict[str, Any]]:
        return self.data
    
    def __repr__(self):
        return repr(self.data)
    
#   Storage Class for Car Damage Data
class CarDamageData:
    def __init__(self):
        self.data: Dict[int, Dict[str, Any]] = {};

    def add_carDamage_Data(self, key: int, carDamageDataString: List[Any]) -> None:

        m_tyresWear = carDamageDataString[0];
        m_tyresDamage = carDamageDataString[1];
        m_brakesDamage = carDamageDataString[2];
        m_frontLeftWingDamage = carDamageDataString[3];
        m_frontRightWingDamage = carDamageDataString[4];
        m_rearWingDamage = carDamageDataString[5];
        m_floorDamage = carDamageDataString[6];
        m_diffuserDamage = carDamageDataString[7];
        m_sidepodDamage = carDamageDataString[8];
        m_drsFault = carDamageDataString[9];
        m_ersFault = carDamageDataString[10];
        m_gearBoxDamage = carDamageDataString[11];
        m_engineDamage = carDamageDataString[12];
        m_engineMGUHWear = carDamageDataString[13];
        m_engineESWear = carDamageDataString[14];   
        m_engineCEWear = carDamageDataString[15];
        m_engineICEWear = carDamageDataString[16];
        m_engineMGUKWear = carDamageDataString[17];
        m_engineTCWear = carDamageDataString[18];
        m_engineBlown = carDamageDataString[19];
        m_engineSeized = carDamageDataString[20];
    
        self.data[key] = {
            'm_tyresWear': m_tyresWear,
            'm_tyresDamage': m_tyresDamage,
            'm_brakesDamage': m_brakesDamage,
            'm_frontLeftWingDamage': m_frontLeftWingDamage,
            'm_frontRightWingDamage': m_frontRightWingDamage,
            'm_rearWingDamage': m_rearWingDamage,
            'm_floorDamage': m_floorDamage,
            'm_diffuserDamage': m_diffuserDamage,
            'm_sidepodDamage': m_sidepodDamage,
            'm_drsFault': m_drsFault,
            'm_ersFault': m_ersFault,
            'm_gearBoxDamage': m_gearBoxDamage,
            'm_engineDamage': m_engineDamage,
            'm_engineMGUHWear': m_engineMGUHWear,
            'm_engineESWear': m_engineESWear,
            'm_engineCEWear': m_engineCEWear,
            'm_engineICEWear': m_engineICEWear,
            'm_engineMGUKWear': m_engineMGUKWear,
            'm_engineTCWear': m_engineTCWear,
            'm_engineBlown': m_engineBlown,
            'm_engineSeized': m_engineSeized,
        };

    def get_carDamage_data_from_key(self, key: int) -> Dict[str, Any]:
        return self.data.get(key)
    
    def get_carDamage_dict(self) -> Dict[int, Dict[str, Any]]:
        return self.data
    
    def __repr__(self):
        return repr(self.data)
    
#   Storage class for Car Telemetry
class CarTelemetry:
    def __init__(self):
        self.data: Dict[int, Dict[str, Any]] = {};
        self.timestamps: Dict[int, int] = {};

    def add_car_telemetry_data(self, key: int, carTelemetryString: List[Any]) -> None:

        if key not in self.data:
            self.timestamps[key] = 0;

        m_speed = carTelemetryString[0];
        m_throttle = carTelemetryString[1];
        m_steer = carTelemetryString[2];
        m_brake = carTelemetryString[3];
        m_clutch = carTelemetryString[4];
        m_gear = carTelemetryString[5];
        m_engineRPM = carTelemetryString[6];
        m_drs = carTelemetryString[7];
        m_revLightsPercent = carTelemetryString[8];
        m_revLightsBitValue = carTelemetryString[9];
        m_brakesTemperature = carTelemetryString[10];
        m_tyresSurfaceTemperature = carTelemetryString[11];
        m_tyresInnerTemperature = carTelemetryString[12];
        m_engineTemperature = carTelemetryString[13];
        m_tyresPressure = carTelemetryString[14];
        m_surfaceType = carTelemetryString[15];

        self.data[key] = {
            'm_speed': m_speed,
            'm_throttle': m_throttle,
            'm_steer': m_steer,
            'm_brake': m_brake,
            'm_clutch': m_clutch,
            'm_gear': m_gear,
            'm_engineRPM': m_engineRPM,
            'm_drs': m_drs,
            'm_revLightsPercent': m_revLightsPercent,
            'm_revLightsBitValue': m_revLightsBitValue,
            'm_brakesTemperature': m_brakesTemperature,
            'm_tyresSurfaceTemperature': m_tyresSurfaceTemperature,
            'm_tyresInnerTemperature': m_tyresInnerTemperature,
            'm_engineTemperature': m_engineTemperature,
            'm_tyresPressure': m_tyresPressure,
            'm_surfaceType': m_surfaceType,
        };
    
        self.timestamps[key] = time.time();

    def get_car_telemetry_data_from_key(self, key:int) -> Dict[str, Any]:
        return self.data.get(key)
    
    def get_car_telemetry_dict(self) -> Dict[int, Dict[str, Any]]:
        return self.data
    
    def __repr__(self):
        return repr(self.data)
    
class PenaltyEvent:
    def init(self):
        self.data: Dict[str, int] = {};

    def add_penalty_data(self, penaltyStr: List[int]) -> None:

        self.data = {
            'penaltyType': penaltyStr[0],
            'infringementType': penaltyStr[1],
            'vehicleIdx': penaltyStr[2],
            'otherVehicleIdx': penaltyStr[3],
            'time': penaltyStr[4],
            'lapNum': penaltyStr[5],
            'placesGained': penaltyStr[6],
        };

    def get_penalty_data_from_key(self, key: str) -> int:
        return self.data.get(key);

    def get_penalty_data_dict(self) -> Dict[str, int]:
        return self.data

    def __repr__(self):
        return repr(self.data);

#   Class which keeps track of the pit status of all the cars
class PitStatusStorage:
    def __init__(self):
        self.current_status = {i: 0 for i in range(22)};
        self.previous_status = {i: 0 for i in range(22)};

    def update_pit_status(self, driverId, status):
        self.previous_status[driverId] = self.current_status[driverId];
        self.current_status[driverId] = status;

    def on_status_change(self, driverId):
        return self.previous_status[driverId] != self.current_status[driverId];

    def get_current_status(self, driverId):
        return self.current_status[driverId];

    def __repr__(self):
        return repr(self.current_status);

#   Car Status Packet
class CarStatusData:
    def __init__(self):
        self.data: Dict[int, Dict[str, Any]] = {};

    def update_car_status_data(self, key: int, carStatusString: List[Any]) -> None:

        m_tractionControl = carStatusString[0];
        m_antiLockBrakes = carStatusString[1];
        m_fuelMix = carStatusString[2];
        m_frontBrakeBias = carStatusString[3];
        m_pitLimiterStatus = carStatusString[4];
        m_fuelInTank = carStatusString[5];
        m_fuelCapacity = carStatusString[6];
        m_fuelRemainingLaps = carStatusString[7];
        m_maxRPM = carStatusString[8];
        m_idleRPM = carStatusString[9];
        m_maxGears = carStatusString[10];
        m_drsAllowed = carStatusString[11];
        m_drsActivationDistance = carStatusString[12];
        m_actualTyreCompound = carStatusString[13];
        m_visualTyreCompound = carStatusString[14];
        m_tyresAgeLaps = carStatusString[15];
        m_vehicleFiaFlags = carStatusString[16];
        m_ersStoreEnergy = carStatusString[17];
        m_ersDeployMode = carStatusString[18];
        m_ersHarvestedThisLapMGUK = carStatusString[19];
        m_ersHarvestedThisLapMGUH = carStatusString[20];
        m_ersDeployedThisLap = carStatusString[21];
        m_networkPaused = carStatusString[22];

        self.data[key] = {
            'm_tractionControl': m_tractionControl,
            'm_antiLockBrakes': m_antiLockBrakes,
            'm_fuelMix': m_fuelMix,
            'm_frontBrakeBias': m_frontBrakeBias,
            'm_pitLimiterStatus': m_pitLimiterStatus,
            'm_fuelInTank': m_fuelInTank,
            'm_fuelCapacity': m_fuelCapacity,
            'm_fuelRemainingLaps': m_fuelRemainingLaps,
            'm_maxRPM': m_maxRPM,
            'm_idleRPM': m_idleRPM,
            'm_maxGears': m_maxGears,
            'm_drsAllowed': m_drsAllowed,
            'm_drsActivationDistance': m_drsActivationDistance,
            'm_actualTyreCompound': m_actualTyreCompound,
            'm_visualTyreCompound': m_visualTyreCompound,
            'm_tyresAgeLaps': m_tyresAgeLaps,
            'm_vehicleFiaFlags': m_vehicleFiaFlags,
            'm_ersStoreEnergy': m_ersStoreEnergy,
            'm_ersDeployMode': m_ersDeployMode,
            'm_ersHarvestedThisLapMGUK': m_ersHarvestedThisLapMGUK,
            'm_ersHarvestedThisLapMGUH': m_ersHarvestedThisLapMGUH,
            'm_ersDeployedThisLap': m_ersDeployedThisLap,
            'm_networkPaused': m_networkPaused,
        };

    def get_car_status_data_from_key(self, key:int) -> Dict[str, Any]:
        return self.data.get(key)
    
    def get_car_status_data_dict(self) -> Dict[int, Dict[str, Any]]:
        return self.data
    
    def __repr__(self):
        return repr(self.data)
    
class CurrentDriverPositions:
    def __init__(self):
        self.data: Dict [int, int] = {};

    def update_current_driver_positions(self, key: int, position: int) -> None:

        self.data = {
            key: position
        };

    def get_current_driver_positions(self) -> Dict[int, int]:
        return self.data;

    def get_current_status_for_driver(self, key: int) -> int:
        return self.data.get(key);