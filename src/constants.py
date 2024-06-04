## Configuration file for the f1-telemetry.py

from enum import Enum
from typing import Dict

IP = "127.0.0.1";	# Change IP if needed
UDP_PORT = 20777;	# Default port for F1 2022

#   Host and Ports for the discord bot IPC
IP_discordIPC = "127.0.0.1";
PORT_discordIPC = 20002;

#   Config params
createJSONFile = True;
createStaticFileName = True;

#   Strings for parsing the structs

p_headerString: str = '<HBBBBQfIBB';
p_finalClassificationPacketString: str = '<BBBBBBIdBBBBBB';
p_participantsPacketString: str = '<BBBBBBB6sB';

#   String for parsing the event data
p_eventTypeString = '<BBBB';
p_eventPenaltyString = '<BBBBBBB';

#Session packet string is split into 5 parts due to custom structs included inside the sessionData struct
p_sessionPacketString_1: str = '<BbbBHBbBHHBBBBBB';
p_sessionPacketString_2: str = '<fb';   # Marshal Zones: Has to be executed 21 times
p_sessionPacketString_3: str = '<BBB';
p_sessionPacketString_4: str = '<BBBbbbbB'; #Weather Forecast Samples: Has to be executed 56 times
p_sessionPacketString_5: str = '<BBIIIBBBBBBBBBBBBBBIB';

#   String to parse lapdata packet
p_lapDataPacketString: str = '<IIHHfffBBBBBBBBBBBBBBHHB';

#   String to parse car damage packet
p_carDamagePacketString_1: str = '<ffff';
p_carDamagePacketString_2: str = '<BBBB';
p_carDamagePacketString_3: str = '<BBBB';
p_carDamagePacketString_4: str = '<BBBBBBBBBBBBBBBBBB';

#String to par car status packet
p_carStatusPacketString: str = '<BBBBBfffHHBBHBBBbfBfffB';

#   String to parse car telemetry packet
p_carTelemetryPacketString_1: str = '<HfffBbHBBH';
p_carTelemetryPacketString_2: str = '<HHHH';
p_carTelemetryPacketString_3: str = '<BBBB';
p_carTelemetryPacketString_4: str = '<BBBB';
p_carTelemetryPacketString_5: str = '<H';
p_carTelemetryPacketString_6: str = '<ffff';
p_carTelemetryPacketString_7: str = '<BBBB';

##  Packet Structures

#   List of packet types

class Packet(Enum):
    MOTION = 0;
    SESSION = 1;
    LAP_DATA = 2;
    EVENT = 3;
    PARTICIPANTS = 4;
    CAR_SETUPS = 5;
    CAR_TELEMETRY = 6;
    CAR_STATUS = 7;
    FINAL_CLASSIFICATION = 8;
    LOBBY_INFO = 9;
    CAR_DAMAGE = 10;
    SESSION_HISTORY = 11;

class EventStringCode(Enum):
    SESSION_STARTED = 'SSTA';
    SESSION_ENDED = 'SEND';
    FASTEST_LAP = 'FTLP';
    RETIREMENT = 'RTMT';
    DRS_ENABLED = 'DRSE';
    DRS_DISABLED = 'DRSD';
    TEAM_MATE_IN_PITS = 'TMPT';
    CHEQUERED_FLAG = 'CHQF';
    RACE_WINNER = 'RCWN';
    PENALTY_ISSUED = 'PENA';
    SPEED_TRAP_TRIGGERED = 'SPTP';
    START_LIGHTS = 'STLG';
    LIGHTS_OUT = 'LGOT';
    DRIVE_THROUGH_SERVED = 'DTSV';
    STOP_GO_SERVED = 'SGSV';
    FLASHBACK = 'FLBK';
    BUTTON_STATUS = 'BUTN';

#   List of track ids

class TrackId(Enum):
    MELBOURNE = 0; 
    PAUL_RICARD = 1;
    SHANGHAI = 2;
    SAKHIR = 3;
    CATALUNYA = 4;
    MONACO = 5;
    MONTREAL = 6;
    SILVERSTONE = 7;
    HOCKENHEIM = 8;
    HUNGARORING = 9;
    SPA = 10;
    MONZA = 11;
    SINGAPORE = 12;
    SUZUKA = 13;
    ABU_DHABI = 14;
    TEXAS = 15;
    BRAZIL = 16;
    AUSTRIA = 17;
    SOCHI = 18;
    MEXICO = 19;
    BAKU = 20;
    SAKHIR_SHORT = 21;
    SILVERSTONE_SHORT = 22;
    TEXAS_SHORT = 23;
    SUZUKA_SHORT = 24;
    HANOI = 25;
    ZANDVOORT = 26;
    IMOLA = 27;
    PORTIMAO = 28;
    JEDDAH = 29;
    MIAMI = 30;

Track_Names: Dict[int, str] = {
    TrackId.MELBOURNE.value: 'Albert Park Circuit',
    TrackId.PAUL_RICARD.value: 'Circuit Paul Ricard',
    TrackId.SHANGHAI.value: 'Shanghai International Circuit',
    TrackId.SAKHIR.value: 'Bahrain International Circuit',
    TrackId.CATALUNYA.value: 'Circuit de Barcelona-Catalunya',
    TrackId.MONACO.value: 'Circuit de Monte Carlo',
    TrackId.MONTREAL.value: 'Circuit Gilles-Villenueve',
    TrackId.SILVERSTONE.value: 'Silverstone Circuit',
    TrackId.HOCKENHEIM.value: 'Hockenheimring',
    TrackId.HUNGARORING.value: 'Hungaroring',
    TrackId.SPA.value: 'Circuit Spa-Francorchamps',
    TrackId.MONZA.value: 'Autodromo Nazionale Monza',
    TrackId.SINGAPORE.value: 'Marina Bay Circuit',
    TrackId.SUZUKA.value: 'Suzuka Circuit',
    TrackId.ABU_DHABI.value: 'Yas Marina Circuit',
    TrackId.TEXAS.value: 'Circuit of the Americas',
    TrackId.BRAZIL.value: 'Autodromo Jose Carlos Pace',
    TrackId.AUSTRIA.value: 'Red Bull Ring',
    TrackId.SOCHI.value: 'Sochi Autodrom',
    TrackId.MEXICO.value: 'Autodromo Hermano Rodriguez',
    TrackId.BAKU.value: 'Baku City Circuit',
    TrackId.SAKHIR_SHORT.value: 'Sakhir Short',
    TrackId.SILVERSTONE_SHORT.value: 'Silverstone Short',
    TrackId.TEXAS_SHORT.value: 'Texas Short',
    TrackId.SUZUKA_SHORT: 'Suzuka Short',
    TrackId.HANOI.value: 'Hanoi Circuit',
    TrackId.ZANDVOORT.value: 'Circuit Zandvoort',
    TrackId.IMOLA.value: 'Autodromo Enzo e Dino Ferrari',
    TrackId.PORTIMAO.value: 'Algarve International Circuit',
    TrackId.JEDDAH.value: 'Jeddah Corniche Circuit',
    TrackId.MIAMI.value: 'Miami International Autodrome', 
};

class SessionType(Enum):
    UNKNOWN = 0;
    P1 = 1;
    P2 = 2;
    P3 = 3;
    SHORT_P = 4;
    Q1 = 5;
    Q2 = 6;
    Q3 = 7;
    SHORT_Q = 8;
    OSQ = 9;
    R = 10;
    R2 = 11;
    R3 = 12;
    TIME_TRIAL = 13;

Session_Type_Name: Dict[int, str] = {
    SessionType.UNKNOWN.value: 'Unknown',
    SessionType.P1.value: 'P1',
    SessionType.P2.value: 'P2',
    SessionType.P3.value: 'P3',
    SessionType.SHORT_P.value: 'Short Practice',
    SessionType.Q1.value: 'Q1',
    SessionType.Q2.value: 'Q2',
    SessionType.Q3.value: 'Q3',
    SessionType.SHORT_Q.value: 'Short Qualifying',
    SessionType.OSQ.value: 'One-Shot Qualifying',
    SessionType.R.value: 'Race',
    SessionType.R2.value: 'Race2',
    SessionType.R3.value: 'Race3',
    SessionType.TIME_TRIAL.value: 'Time Trial',
};

class PenaltyTypes(Enum):
    DRIVE_THROUGH = 0;
    STOP_GO = 1;
    GRID_PENALTY = 2;
    PENALTY_REMINDER = 3;
    TIME_PENALTY = 4;
    WARNING = 5;
    DISQUALIFIED = 6;
    REMOVED_FROM_FORMATION_LAP = 7;
    PARKED_TOO_LONG_TIMER = 8;
    TYRE_REGULATIONS = 9;
    THIS_LAP_INVALIDATED = 10;
    THIS_AND_NEXT_LAP_INVALIDATED = 11;
    THIS_LAP_INVALIDATED_WITHOUT_REASION = 12;
    THIS_AND_NEXT_LAP_INVALIDATED_WITHOUT_REASON = 13;
    THIS_AND_PREVIOUS_LAP_INVALIDATED = 14;
    THIS_AND_PREVIOUS_LAP_INVALIDATED_WITHOUT_REASON = 15;
    RETIRED = 16;
    BLACK_FLAG_TIMER = 17;

PenaltyTypeNames: Dict[int, str] = {
    PenaltyTypes.DRIVE_THROUGH.value: 'Drive Through Penalty',
    PenaltyTypes.STOP_GO.value: 'Stop and Go Penalty',
    PenaltyTypes.GRID_PENALTY.value: 'Grid Penalty',
    PenaltyTypes.PENALTY_REMINDER.value: 'Reminder for the penalty',
    PenaltyTypes.TIME_PENALTY.value: 'Time Penalty',
    PenaltyTypes.WARNING.value: 'Warning',
    PenaltyTypes.DISQUALIFIED.value: 'Disqualified',
    PenaltyTypes.REMOVED_FROM_FORMATION_LAP.value: 'Removed from the formation lap',
    PenaltyTypes.PARKED_TOO_LONG_TIMER.value: 'Parked for too long',
    PenaltyTypes.TYRE_REGULATIONS.value: 'Tyre Regulations Penalty',
    PenaltyTypes.THIS_LAP_INVALIDATED.value: 'This lap invalidated',
    PenaltyTypes.THIS_AND_NEXT_LAP_INVALIDATED.value: 'This and the next lap invalidated',
    PenaltyTypes.THIS_LAP_INVALIDATED_WITHOUT_REASION.value: 'This Lap invalidated without reason',
    PenaltyTypes.THIS_AND_NEXT_LAP_INVALIDATED_WITHOUT_REASON.value: 'This and next lap invalidated without reason',
    PenaltyTypes.THIS_AND_PREVIOUS_LAP_INVALIDATED.value: 'This and previous lap invalidated',
    PenaltyTypes.THIS_AND_PREVIOUS_LAP_INVALIDATED_WITHOUT_REASON.value: 'This and previous lap invalidated without reason',
    PenaltyTypes.RETIRED.value: 'Retired',
    PenaltyTypes.BLACK_FLAG_TIMER.value: 'Black Flag',
};

#   Tyre Compounds
class TyreCompound(Enum):
    SOFT = 16;
    MEDIUM = 17;
    HARD = 18;
    INTERMEDIATE = 7;
    WET = 8;