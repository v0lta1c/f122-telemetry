## Configuration file for the f1-telemetry.py

import os
from enum import Enum
from typing import Dict

IP = "127.0.0.1";	# Change IP if needed
UDP_PORT = 20777;	# Default port for F1 2022
TIMEOUT = 1;       # Timeout for the socket (in seconds)

#   Host and Ports for the discord bot IPC
IP_discordIPC = "84.249.17.176";
PORT_discordIPC = 20002;

webhook_IP = "84.249.17.176";
webhook_PORT = 20003;

# Using Ubuntu font for the gui
# Rights to the font belongs to Ubuntu
font = 'Ubuntu-Regular.ttf';
fonts_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'font'));
FONT_PATH = os.path.join(fonts_dir, font);

#   Config params
createJSONFile = True;
createStaticFileName = True;

POSITION_SAVE_INTERVAL: int = 30;

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

TyreCompoundNames: Dict[int, str] = {

    TyreCompound.SOFT.value: 'Soft',
    TyreCompound.MEDIUM.value: 'Medium',
    TyreCompound.HARD.value: 'Hard',
    TyreCompound.INTERMEDIATE.value: 'Intermediate',
    TyreCompound.WET.value: 'Wet',
}

#   Team Id's 

class TeamId(Enum):
    MERCEDES = 0;
    FERRARI = 1;
    RED_BULL_RACING = 2;
    WILLIAMS = 3;
    ASTON_MARTIN = 4;
    ALPINE = 5;
    ALPHA_TAURI = 6;
    HAAS = 7;
    MCLAREN = 8;
    ALFA_ROMEO = 9;
    MERCEDES_2020 = 85;
    FERRARI_2020 = 86;
    RED_BULL_2020 = 87;
    WILLIAMS_2020 = 88;
    RACING_POINT_2020 = 89;
    RENAULT_2020 = 90;
    ALPHA_TAURI_2020 = 91;
    HAAS_2020 = 92;
    MCLAREN_2020 = 93;
    ALFA_ROMEO_2020 = 94;
    ASTON_MARTIN_DB11_V12 = 95;
    ASTON_MARTIN_VANTAGE_F1_EDITION = 96;
    ASTON_MARTIN_VANTAGE_SAFETY_CAR = 97;
    FERRARI_F8_TRIBUTO = 98;
    FERRARI_ROMA = 99;
    MCLAREN_720S = 100;
    MCLAREN_ARTURA = 101;
    MERCEDES_AMG_GT_BLACK_SERIES_SAFETY_CAR = 102;
    MERCEDES_AMG_GTR_PRO = 103;
    F1_CUSTOM_TEAM = 104;
    PREMA_21 = 106;
    UNI_VIRTUOSI_21 = 107;
    CARLIN_21 = 108;
    HITECH_21 = 109;
    ART_GP_21 = 110;
    MP_MOTORSPORT_21 = 111;
    CHAROUZ_21 = 112;
    DAMS_21 = 113;
    CAMPOS_21 = 114;
    BWT_21 = 115;
    TRIDENT_21 = 116;
    MERCEDES_AMG_GT_BLACK_SERIES = 117;
    PREMA_22 = 118;
    VIRTUOSI_22 = 119;
    CARLIN_22 = 120;
    HITECH_22 = 121;
    ART_GP_22 = 122;
    MP_MOTORSPORT_22 = 123;
    CHAROUZ_22 = 124;
    DAMS_22 = 125;
    CAMPOS_22 = 126;
    VAN_AMERSFOORT_RACING_22 = 127;
    TRIDENT_22 = 128;

TeamNames: Dict[int, str] = {

    TeamId.MERCEDES.value: 'Mercedes',
    TeamId.FERRARI.value: 'Ferrari',
    TeamId.RED_BULL_RACING.value: 'Red Bull Racing',
    TeamId.WILLIAMS.value: 'Williams',
    TeamId.ASTON_MARTIN.value: 'Aston Martin',
    TeamId.ALPINE.value: 'Alpine',
    TeamId.ALPHA_TAURI.value: 'Alpha Tauri',
    TeamId.HAAS.value: 'Haas',
    TeamId.MCLAREN.value: 'McLaren',
    TeamId.ALFA_ROMEO.value: 'Alfa Romeo',
    TeamId.MERCEDES_2020.value: 'Mercedes 2020',
    TeamId.FERRARI_2020.value: 'Ferrari 2020',
    TeamId.RED_BULL_2020.value: 'Red Bull 2020',
    TeamId.WILLIAMS_2020.value: 'Williams 2020',
    TeamId.RACING_POINT_2020.value: 'Racing Point 2020',
    TeamId.RENAULT_2020.value: 'Renault 2020',
    TeamId.ALPHA_TAURI_2020.value: 'Alpha Tauri 2020',
    TeamId.HAAS_2020.value: 'Haas 2020',
    TeamId.MCLAREN_2020.value: 'McLaren 2020',
    TeamId.ALFA_ROMEO_2020.value: 'Alfa Romeo 2020',
    TeamId.ASTON_MARTIN_DB11_V12.value: 'Aston Martin DB11 V12',
    TeamId.ASTON_MARTIN_VANTAGE_F1_EDITION.value: 'Aston Martin Vantage F1 Edition',
    TeamId.ASTON_MARTIN_VANTAGE_SAFETY_CAR.value: 'Aston Martin Vantage Safety Car',
    TeamId.FERRARI_F8_TRIBUTO.value: 'Ferrari F8 Tributo',
    TeamId.FERRARI_ROMA.value: 'Ferrari Roma',
    TeamId.MCLAREN_720S.value: 'McLaren 720S',
    TeamId.MCLAREN_ARTURA.value: 'McLaren Artura',
    TeamId.MERCEDES_AMG_GT_BLACK_SERIES_SAFETY_CAR.value: 'Mercedes AMG GT Black Series Safety Car',
    TeamId.MERCEDES_AMG_GTR_PRO.value: 'Mercedes AMG GTR Pro',
    TeamId.F1_CUSTOM_TEAM.value: 'F1 Custom Team',
    TeamId.PREMA_21.value: "Prema '21",
    TeamId.UNI_VIRTUOSI_21.value: "Uni-Virtuosi '21",
    TeamId.CARLIN_21.value: "Carlin '21",
    TeamId.HITECH_21.value: "Hitech '21",
    TeamId.ART_GP_21.value: "Art GP '21",
    TeamId.MP_MOTORSPORT_21.value: "MP Motorsport '21",
    TeamId.CHAROUZ_21.value: "Charouz '21",
    TeamId.DAMS_21.value: "Dams '21",
    TeamId.CAMPOS_21.value: "Campos '21",
    TeamId.BWT_21.value: "BWT '21",
    TeamId.TRIDENT_21.value: "Trident '21",
    TeamId.MERCEDES_AMG_GT_BLACK_SERIES.value: "Mercedes AMG GT Black Series",
    TeamId.PREMA_22.value: "Prema '22",
    TeamId.VIRTUOSI_22.value: "Virtuosi '22",
    TeamId.CARLIN_22.value: "Carlin '22",
    TeamId.HITECH_22.value: "Hitech '22",
    TeamId.ART_GP_22.value: "Art GP '22",
    TeamId.MP_MOTORSPORT_22.value: "MP Motorsport '22",
    TeamId.CHAROUZ_22.value: "Charouz '22",
    TeamId.DAMS_22.value: "Dams '22",
    TeamId.CAMPOS_22.value: "Campos '22",
    TeamId.VAN_AMERSFOORT_RACING_22.value: "Van Amersfoort Racing '22",
    TeamId.TRIDENT_22.value: "Trident '22",
};
    