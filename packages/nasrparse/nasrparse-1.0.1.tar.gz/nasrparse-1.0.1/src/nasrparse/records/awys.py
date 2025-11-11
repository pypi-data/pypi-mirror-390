from nasrparse.records.awy import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.awy import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class AWYs:
    __dir_path: str

    awy_alt: list[AWY_ALT]
    awy_base: list[AWY_BASE]
    awy_seg: list[AWY_SEG]
    awy_seg_alt: list[AWY_SEG_ALT]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.awy_alt = []
        self.awy_base = []
        self.awy_seg = []
        self.awy_seg_alt = []

    def parse(self) -> None:
        self.parse_awy_alt()
        self.parse_awy_base()
        self.parse_awy_seg()
        self.parse_awy_seg_alt()

    def parse_awy_alt(self) -> None:
        file_path = path.join(self.__dir_path, AWY_ALT_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {AWY_ALT_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = AWY_ALT(
                    eff_date=row["EFF_DATE"],
                    regulatory=row["REGULATORY"],
                    awy_location=row["AWY_LOCATION"],
                    awy_id=row["AWY_ID"],
                    point_seq=row["POINT_SEQ"],
                    mea_pt=row["MEA_PT"],
                    mea_pt_type=row["MEA_PT_TYPE"],
                    nav_name=row["NAV_NAME"],
                    nav_city=row["NAV_CITY"],
                    icao_region_code=row["ICAO_REGION_CODE"],
                    state_code=row["STATE_CODE"],
                    country_code=row["COUNTRY_CODE"],
                    next_mea_pt=row["NEXT_MEA_PT"],
                    min_enroute_alt=row["MIN_ENROUTE_ALT"],
                    min_enroute_alt_dir=row["MIN_ENROUTE_ALT_DIR"],
                    min_enroute_alt_opposite=row["MIN_ENROUTE_ALT_OPPOSITE"],
                    min_enroute_alt_opposite_dir=row["MIN_ENROUTE_ALT_OPPOSITE_DIR"],
                    gps_min_enroute_alt=row["GPS_MIN_ENROUTE_ALT"],
                    gps_min_enroute_alt_dir=row["GPS_MIN_ENROUTE_ALT_DIR"],
                    gps_min_enroute_alt_opposite=row["GPS_MIN_ENROUTE_ALT_OPPOSITE"],
                    gps_mea_opposite_dir=row["GPS_MEA_OPPOSITE_DIR"],
                    dd_iru_mea=row["DD_IRU_MEA"],
                    dd_iru_mea_dir=row["DD_IRU_MEA_DIR"],
                    dd_i_mea_opposite=row["DD_I_MEA_OPPOSITE"],
                    dd_i_mea_opposite_dir=row["DD_I_MEA_OPPOSITE_DIR"],
                    min_obstn_clnc_alt=row["MIN_OBSTN_CLNC_ALT"],
                    min_cross_alt=row["MIN_CROSS_ALT"],
                    min_cross_alt_dir=row["MIN_CROSS_ALT_DIR"],
                    min_cross_alt_nav_pt=row["MIN_CROSS_ALT_NAV_PT"],
                    min_cross_alt_opposite=row["MIN_CROSS_ALT_OPPOSITE"],
                    min_cross_alt_opposite_dir=row["MIN_CROSS_ALT_OPPOSITE_DIR"],
                    min_recep_alt=row["MIN_RECEP_ALT"],
                    max_auth_alt=row["MAX_AUTH_ALT"],
                    mea_gap=row["MEA_GAP"],
                    reqd_nav_performance=row["REQD_NAV_PERFORMANCE"],
                    remark=row["REMARK"],
                )
                self.awy_alt.append(record)

    def parse_awy_base(self) -> None:
        file_path = path.join(self.__dir_path, AWY_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {AWY_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = AWY_BASE(
                    eff_date=row["EFF_DATE"],
                    regulatory=row["REGULATORY"],
                    awy_location=row["AWY_LOCATION"],
                    awy_id=row["AWY_ID"],
                    awy_designation=row["AWY_DESIGNATION"],
                    update_date=row["UPDATE_DATE"],
                    remark=row["REMARK"],
                    airway_string=row["AIRWAY_STRING"],
                )
                self.awy_base.append(record)

    def parse_awy_seg(self) -> None:
        file_path = path.join(self.__dir_path, AWY_SEG_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {AWY_SEG_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = AWY_SEG(
                    eff_date=row["EFF_DATE"],
                    regulatory=row["REGULATORY"],
                    awy_location=row["AWY_LOCATION"],
                    awy_id=row["AWY_ID"],
                    point_seq=row["POINT_SEQ"],
                    seg_value=row["SEG_VALUE"],
                    seg_type=row["SEG_TYPE"],
                    nav_name=row["NAV_NAME"],
                    nav_city=row["NAV_CITY"],
                    icao_region_code=row["ICAO_REGION_CODE"],
                    state_code=row["STATE_CODE"],
                    country_code=row["COUNTRY_CODE"],
                    next_seg=row["NEXT_SEG"],
                    mag_course=row["MAG_COURSE"],
                    opp_mag_course=row["OPP_MAG_COURSE"],
                    mag_course_dist=row["MAG_COURSE_DIST"],
                    chgovr_pt=row["CHGOVR_PT"],
                    chgovr_pt_name=row["CHGOVR_PT_NAME"],
                    chgovr_pt_dist=row["CHGOVR_PT_DIST"],
                    awy_seg_gap_flag=row["AWY_SEG_GAP_FLAG"],
                    signal_gap_flag=row["SIGNAL_GAP_FLAG"],
                    dogleg=row["DOGLEG"],
                    remark=row["REMARK"],
                )
                self.awy_seg.append(record)

    def parse_awy_seg_alt(self) -> None:
        file_path = path.join(self.__dir_path, AWY_SEG_ALT_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {AWY_SEG_ALT_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = AWY_SEG_ALT(
                    eff_date=row["EFF_DATE"],
                    regulatory=row["REGULATORY"],
                    awy_location=row["AWY_LOCATION"],
                    awy_id=row["AWY_ID"],
                    point_seq=row["POINT_SEQ"],
                    from_point=row["FROM_POINT"],
                    from_pt_type=row["FROM_PT_TYPE"],
                    nav_name=row["NAV_NAME"],
                    nav_city=row["NAV_CITY"],
                    artcc=row["ARTCC"],
                    icao_region_code=row["ICAO_REGION_CODE"],
                    state_code=row["STATE_CODE"],
                    country_code=row["COUNTRY_CODE"],
                    to_point=row["TO_POINT"],
                    mag_course=row["MAG_COURSE"],
                    opp_mag_course=row["OPP_MAG_COURSE"],
                    mag_course_dist=row["MAG_COURSE_DIST"],
                    chgovr_pt=row["CHGOVR_PT"],
                    chgovr_pt_name=row["CHGOVR_PT_NAME"],
                    chgovr_pt_dist=row["CHGOVR_PT_DIST"],
                    awy_seg_gap_flag=row["AWY_SEG_GAP_FLAG"],
                    signal_gap_flag=row["SIGNAL_GAP_FLAG"],
                    dogleg=row["DOGLEG"],
                    next_mea_pt=row["NEXT_MEA_PT"],
                    min_enroute_alt=row["MIN_ENROUTE_ALT"],
                    min_enroute_alt_dir=row["MIN_ENROUTE_ALT_DIR"],
                    min_enroute_alt_opposite=row["MIN_ENROUTE_ALT_OPPOSITE"],
                    min_enroute_alt_opposite_dir=row["MIN_ENROUTE_ALT_OPPOSITE_DIR"],
                    gps_min_enroute_alt=row["GPS_MIN_ENROUTE_ALT"],
                    gps_min_enroute_alt_dir=row["GPS_MIN_ENROUTE_ALT_DIR"],
                    gps_min_enroute_alt_opposite=row["GPS_MIN_ENROUTE_ALT_OPPOSITE"],
                    gps_mea_opposite_dir=row["GPS_MEA_OPPOSITE_DIR"],
                    dd_iru_mea=row["DD_IRU_MEA"],
                    dd_iru_mea_dir=row["DD_IRU_MEA_DIR"],
                    dd_i_mea_opposite=row["DD_I_MEA_OPPOSITE"],
                    dd_i_mea_opposite_dir=row["DD_I_MEA_OPPOSITE_DIR"],
                    min_obstn_clnc_alt=row["MIN_OBSTN_CLNC_ALT"],
                    min_cross_alt=row["MIN_CROSS_ALT"],
                    min_cross_alt_dir=row["MIN_CROSS_ALT_DIR"],
                    min_cross_alt_nav_pt=row["MIN_CROSS_ALT_NAV_PT"],
                    min_cross_alt_opposite=row["MIN_CROSS_ALT_OPPOSITE"],
                    min_cross_alt_opposite_dir=row["MIN_CROSS_ALT_OPPOSITE_DIR"],
                    min_recep_alt=row["MIN_RECEP_ALT"],
                    max_auth_alt=row["MAX_AUTH_ALT"],
                    mea_gap=row["MEA_GAP"],
                    reqd_nav_performance=row["REQD_NAV_PERFORMANCE"],
                    remark=row["REMARK"],
                )
                self.awy_seg_alt.append(record)

    def to_dict(self) -> dict:
        return {
            **self.awy_alt_to_dict(),
            **self.awy_base_to_dict(),
            **self.awy_seg_to_dict(),
            **self.awy_seg_alt_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.awy_alt_to_db(db_cursor)
        self.awy_base_to_db(db_cursor)
        self.awy_seg_to_db(db_cursor)
        self.awy_seg_alt_to_db(db_cursor)

    def awy_alt_to_dict(self) -> dict:
        return {"awy_alt": [item.to_dict() for item in self.awy_alt]}

    def awy_base_to_dict(self) -> dict:
        return {"awy_base": [item.to_dict() for item in self.awy_base]}

    def awy_seg_to_dict(self) -> dict:
        return {"awy_seg": [item.to_dict() for item in self.awy_seg]}

    def awy_seg_alt_to_dict(self) -> dict:
        return {"awy_seg_alt": [item.to_dict() for item in self.awy_seg_alt]}

    def awy_alt_to_db(self, db_cursor: Cursor) -> None:
        if len(self.awy_alt) > 0:
            print(f"               Processing {AWY_ALT_FILE_NAME}")
            process_table(db_cursor, self.awy_alt)

    def awy_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.awy_base) > 0:
            print(f"               Processing {AWY_BASE_FILE_NAME}")
            process_table(db_cursor, self.awy_base)

    def awy_seg_to_db(self, db_cursor: Cursor) -> None:
        if len(self.awy_seg) > 0:
            print(f"               Processing {AWY_SEG_FILE_NAME}")
            process_table(db_cursor, self.awy_seg)

    def awy_seg_alt_to_db(self, db_cursor: Cursor) -> None:
        if len(self.awy_seg_alt) > 0:
            print(f"               Processing {AWY_SEG_ALT_FILE_NAME}")
            process_table(db_cursor, self.awy_seg_alt)
