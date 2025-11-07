from nasrparse.records.ils import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.ils import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class ILSs:
    __dir_path: str

    ils_base: list[ILS_BASE]
    ils_dme: list[ILS_DME]
    ils_gs: list[ILS_GS]
    ils_mkr: list[ILS_MKR]
    ils_rmk: list[ILS_RMK]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.ils_base = []
        self.ils_dme = []
        self.ils_gs = []
        self.ils_mkr = []
        self.ils_rmk = []

    def parse(self) -> None:
        self.parse_ils_base()
        self.parse_ils_dme()
        self.parse_ils_gs()
        self.parse_ils_mkr()
        self.parse_ils_rmk()

    def parse_ils_base(self) -> None:
        file_path = path.join(self.__dir_path, ILS_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {ILS_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = ILS_BASE(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    state_code=row["STATE_CODE"],
                    arpt_id=row["ARPT_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    rwy_end_id=row["RWY_END_ID"],
                    ils_loc_id=row["ILS_LOC_ID"],
                    system_type_code=row["SYSTEM_TYPE_CODE"],
                    state_name=row["STATE_NAME"],
                    region_code=row["REGION_CODE"],
                    rwy_len=row["RWY_LEN"],
                    rwy_width=row["RWY_WIDTH"],
                    category=row["CATEGORY"],
                    owner=row["OWNER"],
                    operator=row["OPERATOR"],
                    apch_bear=row["APCH_BEAR"],
                    mag_var=row["MAG_VAR"],
                    mag_var_hemis=row["MAG_VAR_HEMIS"],
                    component_status=row["COMPONENT_STATUS"],
                    component_status_date=row["COMPONENT_STATUS_DATE"],
                    lat_deg=row["LAT_DEG"],
                    lat_min=row["LAT_MIN"],
                    lat_sec=row["LAT_SEC"],
                    lat_hemis=row["LAT_HEMIS"],
                    lat_decimal=row["LAT_DECIMAL"],
                    lon_deg=row["LONG_DEG"],
                    lon_min=row["LONG_MIN"],
                    lon_sec=row["LONG_SEC"],
                    lon_hemis=row["LONG_HEMIS"],
                    lon_decimal=row["LONG_DECIMAL"],
                    lat_lon_source_code=row["LAT_LONG_SOURCE_CODE"],
                    site_elevation=row["SITE_ELEVATION"],
                    loc_freq=row["LOC_FREQ"],
                    bk_course_status_code=row["BK_COURSE_STATUS_CODE"],
                )
                self.ils_base.append(record)

    def parse_ils_dme(self) -> None:
        file_path = path.join(self.__dir_path, ILS_DME_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {ILS_DME_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = ILS_DME(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    state_code=row["STATE_CODE"],
                    arpt_id=row["ARPT_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    rwy_end_id=row["RWY_END_ID"],
                    ils_loc_id=row["ILS_LOC_ID"],
                    system_type_code=row["SYSTEM_TYPE_CODE"],
                    component_status=row["COMPONENT_STATUS"],
                    component_status_date=row["COMPONENT_STATUS_DATE"],
                    lat_deg=row["LAT_DEG"],
                    lat_min=row["LAT_MIN"],
                    lat_sec=row["LAT_SEC"],
                    lat_hemis=row["LAT_HEMIS"],
                    lat_decimal=row["LAT_DECIMAL"],
                    lon_deg=row["LONG_DEG"],
                    lon_min=row["LONG_MIN"],
                    lon_sec=row["LONG_SEC"],
                    lon_hemis=row["LONG_HEMIS"],
                    lon_decimal=row["LONG_DECIMAL"],
                    lat_lon_source_code=row["LAT_LONG_SOURCE_CODE"],
                    site_elevation=row["SITE_ELEVATION"],
                    channel=row["CHANNEL"],
                )
                self.ils_dme.append(record)

    def parse_ils_gs(self) -> None:
        file_path = path.join(self.__dir_path, ILS_GS_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {ILS_GS_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = ILS_GS(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    state_code=row["STATE_CODE"],
                    arpt_id=row["ARPT_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    rwy_end_id=row["RWY_END_ID"],
                    ils_loc_id=row["ILS_LOC_ID"],
                    system_type_code=row["SYSTEM_TYPE_CODE"],
                    component_status=row["COMPONENT_STATUS"],
                    component_status_date=row["COMPONENT_STATUS_DATE"],
                    lat_deg=row["LAT_DEG"],
                    lat_min=row["LAT_MIN"],
                    lat_sec=row["LAT_SEC"],
                    lat_hemis=row["LAT_HEMIS"],
                    lat_decimal=row["LAT_DECIMAL"],
                    lon_deg=row["LONG_DEG"],
                    lon_min=row["LONG_MIN"],
                    lon_sec=row["LONG_SEC"],
                    lon_hemis=row["LONG_HEMIS"],
                    lon_decimal=row["LONG_DECIMAL"],
                    lat_lon_source_code=row["LAT_LONG_SOURCE_CODE"],
                    site_elevation=row["SITE_ELEVATION"],
                    g_s_type_code=row["G_S_TYPE_CODE"],
                    g_s_angle=row["G_S_ANGLE"],
                    g_s_freq=row["G_S_FREQ"],
                )
                self.ils_gs.append(record)

    def parse_ils_mkr(self) -> None:
        file_path = path.join(self.__dir_path, ILS_MKR_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {ILS_MKR_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = ILS_MKR(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    state_code=row["STATE_CODE"],
                    arpt_id=row["ARPT_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    rwy_end_id=row["RWY_END_ID"],
                    ils_loc_id=row["ILS_LOC_ID"],
                    system_type_code=row["SYSTEM_TYPE_CODE"],
                    ils_comp_type_code=row["ILS_COMP_TYPE_CODE"],
                    component_status=row["COMPONENT_STATUS"],
                    component_status_date=row["COMPONENT_STATUS_DATE"],
                    lat_deg=row["LAT_DEG"],
                    lat_min=row["LAT_MIN"],
                    lat_sec=row["LAT_SEC"],
                    lat_hemis=row["LAT_HEMIS"],
                    lat_decimal=row["LAT_DECIMAL"],
                    lon_deg=row["LONG_DEG"],
                    lon_min=row["LONG_MIN"],
                    lon_sec=row["LONG_SEC"],
                    lon_hemis=row["LONG_HEMIS"],
                    lon_decimal=row["LONG_DECIMAL"],
                    lat_lon_source_code=row["LAT_LONG_SOURCE_CODE"],
                    site_elevation=row["SITE_ELEVATION"],
                    mkr_fac_type_code=row["MKR_FAC_TYPE_CODE"],
                    marker_id_beacon=row["MARKER_ID_BEACON"],
                    compass_locator_name=row["COMPASS_LOCATOR_NAME"],
                    freq=row["FREQ"],
                    nav_id=row["NAV_ID"],
                    nav_type=row["NAV_TYPE"],
                    low_powered_ndb_status=row["LOW_POWERED_NDB_STATUS"],
                )
                self.ils_mkr.append(record)

    def parse_ils_rmk(self) -> None:
        file_path = path.join(self.__dir_path, ILS_RMK_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {ILS_RMK_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = ILS_RMK(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    state_code=row["STATE_CODE"],
                    arpt_id=row["ARPT_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    rwy_end_id=row["RWY_END_ID"],
                    ils_loc_id=row["ILS_LOC_ID"],
                    system_type_code=row["SYSTEM_TYPE_CODE"],
                    tab_name=row["TAB_NAME"],
                    ils_comp_type_code=row["ILS_COMP_TYPE_CODE"],
                    ref_col_name=row["REF_COL_NAME"],
                    ref_col_seq_no=row["REF_COL_SEQ_NO"],
                    remark=row["REMARK"],
                )
                self.ils_rmk.append(record)

    def to_dict(self) -> dict:
        return {
            **self.ils_base_to_dict(),
            **self.ils_dme_to_dict(),
            **self.ils_gs_to_dict(),
            **self.ils_mkr_to_dict(),
            **self.ils_rmk_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.ils_base_to_db(db_cursor)
        self.ils_dme_to_db(db_cursor)
        self.ils_gs_to_db(db_cursor)
        self.ils_mkr_to_db(db_cursor)
        self.ils_rmk_to_db(db_cursor)

    def ils_base_to_dict(self) -> dict:
        return {"ils_base": [item.to_dict() for item in self.ils_base]}

    def ils_dme_to_dict(self) -> dict:
        return {"ils_dme": [item.to_dict() for item in self.ils_dme]}

    def ils_gs_to_dict(self) -> dict:
        return {"ils_gs": [item.to_dict() for item in self.ils_gs]}

    def ils_mkr_to_dict(self) -> dict:
        return {"ils_mkr": [item.to_dict() for item in self.ils_mkr]}

    def ils_rmk_to_dict(self) -> dict:
        return {"ils_rmk": [item.to_dict() for item in self.ils_rmk]}

    def ils_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.ils_base) > 0:
            print(f"               Processing {ILS_BASE_FILE_NAME}")
            process_table(db_cursor, self.ils_base)

    def ils_dme_to_db(self, db_cursor: Cursor) -> None:
        if len(self.ils_dme) > 0:
            print(f"               Processing {ILS_DME_FILE_NAME}")
            process_table(db_cursor, self.ils_dme)

    def ils_gs_to_db(self, db_cursor: Cursor) -> None:
        if len(self.ils_gs) > 0:
            print(f"               Processing {ILS_GS_FILE_NAME}")
            process_table(db_cursor, self.ils_gs)

    def ils_mkr_to_db(self, db_cursor: Cursor) -> None:
        if len(self.ils_mkr) > 0:
            print(f"               Processing {ILS_MKR_FILE_NAME}")
            process_table(db_cursor, self.ils_mkr)

    def ils_rmk_to_db(self, db_cursor: Cursor) -> None:
        if len(self.ils_rmk) > 0:
            print(f"               Processing {ILS_RMK_FILE_NAME}")
            process_table(db_cursor, self.ils_rmk)
