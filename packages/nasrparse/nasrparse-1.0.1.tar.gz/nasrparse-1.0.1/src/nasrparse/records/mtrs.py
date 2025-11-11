from nasrparse.records.mtr import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.mtr import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class MTRs:
    __dir_path: str

    mtr_agy: list[MTR_AGY]
    mtr_base: list[MTR_BASE]
    mtr_pt: list[MTR_PT]
    mtr_sop: list[MTR_SOP]
    mtr_terr: list[MTR_TERR]
    mtr_wdth: list[MTR_WDTH]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.mtr_agy = []
        self.mtr_base = []
        self.mtr_pt = []
        self.mtr_sop = []
        self.mtr_terr = []
        self.mtr_wdth = []

    def parse(self) -> None:
        self.parse_mtr_agy()
        self.parse_mtr_base()
        self.parse_mtr_pt()
        self.parse_mtr_sop()
        self.parse_mtr_terr()
        self.parse_mtr_wdth()

    def parse_mtr_agy(self) -> None:
        file_path = path.join(self.__dir_path, MTR_AGY_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MTR_AGY_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MTR_AGY(
                    eff_date=row["EFF_DATE"],
                    route_type_code=row["ROUTE_TYPE_CODE"],
                    route_id=row["ROUTE_ID"],
                    artcc=row["ARTCC"],
                    agency_type=row["AGENCY_TYPE"],
                    agency_name=row["AGENCY_NAME"],
                    station=row["STATION"],
                    address=row["ADDRESS"],
                    city=row["CITY"],
                    state_code=row["STATE_CODE"],
                    zip_code=row["ZIP_CODE"],
                    commercial_no=row["COMMERCIAL_NO"],
                    dsn_no=row["DSN_NO"],
                    hours=row["HOURS"],
                )
                self.mtr_agy.append(record)

    def parse_mtr_base(self) -> None:
        file_path = path.join(self.__dir_path, MTR_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MTR_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MTR_BASE(
                    eff_date=row["EFF_DATE"],
                    route_type_code=row["ROUTE_TYPE_CODE"],
                    route_id=row["ROUTE_ID"],
                    artcc=row["ARTCC"],
                    fss=row["FSS"],
                    time_of_use=row["TIME_OF_USE"],
                )
                self.mtr_base.append(record)

    def parse_mtr_pt(self) -> None:
        file_path = path.join(self.__dir_path, MTR_PT_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MTR_PT_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MTR_PT(
                    eff_date=row["EFF_DATE"],
                    route_type_code=row["ROUTE_TYPE_CODE"],
                    route_id=row["ROUTE_ID"],
                    artcc=row["ARTCC"],
                    route_pt_seq=row["ROUTE_PT_SEQ"],
                    route_pt_id=row["ROUTE_PT_ID"],
                    next_route_pt_id=row["NEXT_ROUTE_PT_ID"],
                    segment_text=row["SEGMENT_TEXT"],
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
                    nav_id=row["NAV_ID"],
                    navaid_bearing=row["NAVAID_BEARING"],
                    navaid_dist=row["NAVAID_DIST"],
                )
                self.mtr_pt.append(record)

    def parse_mtr_sop(self) -> None:
        file_path = path.join(self.__dir_path, MTR_SOP_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MTR_SOP_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MTR_SOP(
                    eff_date=row["EFF_DATE"],
                    route_type_code=row["ROUTE_TYPE_CODE"],
                    route_id=row["ROUTE_ID"],
                    artcc=row["ARTCC"],
                    sop_seq_no=row["SOP_SEQ_NO"],
                    sop_text=row["SOP_TEXT"],
                )
                self.mtr_sop.append(record)

    def parse_mtr_terr(self) -> None:
        file_path = path.join(self.__dir_path, MTR_TERR_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MTR_TERR_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MTR_TERR(
                    eff_date=row["EFF_DATE"],
                    route_type_code=row["ROUTE_TYPE_CODE"],
                    route_id=row["ROUTE_ID"],
                    artcc=row["ARTCC"],
                    terrain_seq_no=row["TERRAIN_SEQ_NO"],
                    terrain_text=row["TERRAIN_TEXT"],
                )
                self.mtr_terr.append(record)

    def parse_mtr_wdth(self) -> None:
        file_path = path.join(self.__dir_path, MTR_WDTH_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MTR_WDTH_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MTR_WDTH(
                    eff_date=row["EFF_DATE"],
                    route_type_code=row["ROUTE_TYPE_CODE"],
                    route_id=row["ROUTE_ID"],
                    artcc=row["ARTCC"],
                    width_seq_no=row["WIDTH_SEQ_NO"],
                    width_text=row["WIDTH_TEXT"],
                )
                self.mtr_wdth.append(record)

    def to_dict(self) -> dict:
        return {
            **self.mtr_agy_to_dict(),
            **self.mtr_base_to_dict(),
            **self.mtr_pt_to_dict(),
            **self.mtr_sop_to_dict(),
            **self.mtr_terr_to_dict(),
            **self.mtr_wdth_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.mtr_agy_to_db(db_cursor)
        self.mtr_base_to_db(db_cursor)
        self.mtr_pt_to_db(db_cursor)
        self.mtr_sop_to_db(db_cursor)
        self.mtr_terr_to_db(db_cursor)
        self.mtr_wdth_to_db(db_cursor)

    def mtr_agy_to_dict(self) -> dict:
        return {"mtr_agy": [item.to_dict() for item in self.mtr_agy]}

    def mtr_base_to_dict(self) -> dict:
        return {"mtr_base": [item.to_dict() for item in self.mtr_base]}

    def mtr_pt_to_dict(self) -> dict:
        return {"mtr_pt": [item.to_dict() for item in self.mtr_pt]}

    def mtr_sop_to_dict(self) -> dict:
        return {"mtr_sop": [item.to_dict() for item in self.mtr_sop]}

    def mtr_terr_to_dict(self) -> dict:
        return {"mtr_terr": [item.to_dict() for item in self.mtr_terr]}

    def mtr_wdth_to_dict(self) -> dict:
        return {"mtr_wdth": [item.to_dict() for item in self.mtr_wdth]}

    def mtr_agy_to_db(self, db_cursor: Cursor) -> None:
        if len(self.mtr_agy) > 0:
            print(f"               Processing {MTR_AGY_FILE_NAME}")
            process_table(db_cursor, self.mtr_agy)

    def mtr_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.mtr_base) > 0:
            print(f"               Processing {MTR_BASE_FILE_NAME}")
            process_table(db_cursor, self.mtr_base)

    def mtr_pt_to_db(self, db_cursor: Cursor) -> None:
        if len(self.mtr_pt) > 0:
            print(f"               Processing {MTR_PT_FILE_NAME}")
            process_table(db_cursor, self.mtr_pt)

    def mtr_sop_to_db(self, db_cursor: Cursor) -> None:
        if len(self.mtr_sop) > 0:
            print(f"               Processing {MTR_SOP_FILE_NAME}")
            process_table(db_cursor, self.mtr_sop)

    def mtr_terr_to_db(self, db_cursor: Cursor) -> None:
        if len(self.mtr_terr) > 0:
            print(f"               Processing {MTR_TERR_FILE_NAME}")
            process_table(db_cursor, self.mtr_terr)

    def mtr_wdth_to_db(self, db_cursor: Cursor) -> None:
        if len(self.mtr_wdth) > 0:
            print(f"               Processing {MTR_WDTH_FILE_NAME}")
            process_table(db_cursor, self.mtr_wdth)
