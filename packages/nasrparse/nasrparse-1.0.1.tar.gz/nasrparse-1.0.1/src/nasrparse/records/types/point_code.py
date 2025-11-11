from ._base_enum import BaseEnum


class PointCode(BaseEnum):
    COMPUTER_NAVIGATION_FIX = "CN"
    MILITARY_REPORTING_POINT = "MR"
    MILITARY_WAYPOINT = "MW"
    NRS_WAYPOINT = "NRS"
    RADAR = "RADAR"
    REPORTING_POINT = "RP"
    VFR_WAYPOINT = "VFR"
    WAYPOINT = "WP"
    CONSOLAN = "CONSOLAN"
    DME = "DME"
    FAN_MARKER = "FAN MARKER"
    MARINE_NDB = "MARINE NDB"
    MARINE_NDB_DME = "MARINE NDB/DME"
    NDB = "NDB"
    NDB_DME = "NDB/DME"
    TACAN = "TACAN"
    UHF_NDB = "UHF/NDB"
    VOR = "VOR"
    VORTAC = "VORTAC"
    VOR_DME = "VOR/DME"
    VOT = "VOT"
    NULL = None
