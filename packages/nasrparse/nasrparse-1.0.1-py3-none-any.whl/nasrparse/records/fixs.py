from nasrparse.records.fix import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.fix import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class FIXs:
    __dir_path: str

    fix_base: list[FIX_BASE]
    fix_chrt: list[FIX_CHRT]
    fix_nav: list[FIX_NAV]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.fix_base = []
        self.fix_chrt = []
        self.fix_nav = []

    def parse(self) -> None:
        self.parse_fix_base()
        self.parse_fix_chrt()
        self.parse_fix_nav()

    def parse_fix_base(self) -> None:
        file_path = path.join(self.__dir_path, FIX_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {FIX_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = FIX_BASE(
                    eff_date=row["EFF_DATE"],
                    fix_id=row["FIX_ID"],
                    icao_region_code=row["ICAO_REGION_CODE"],
                    state_code=row["STATE_CODE"],
                    country_code=row["COUNTRY_CODE"],
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
                    fix_id_old=row["FIX_ID_OLD"],
                    charting_remark=row["CHARTING_REMARK"],
                    fix_use_code=row["FIX_USE_CODE"],
                    artcc_id_high=row["ARTCC_ID_HIGH"],
                    artcc_id_low=row["ARTCC_ID_LOW"],
                    pitch_flag=row["PITCH_FLAG"],
                    catch_flag=row["CATCH_FLAG"],
                    sua_atcaa_flag=row["SUA_ATCAA_FLAG"],
                    min_recep_alt=row["MIN_RECEP_ALT"],
                    compulsory=row["COMPULSORY"],
                    charts=row["CHARTS"],
                )
                self.fix_base.append(record)

    def parse_fix_chrt(self) -> None:
        file_path = path.join(self.__dir_path, FIX_CHRT_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {FIX_CHRT_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = FIX_CHRT(
                    eff_date=row["EFF_DATE"],
                    fix_id=row["FIX_ID"],
                    icao_region_code=row["ICAO_REGION_CODE"],
                    state_code=row["STATE_CODE"],
                    country_code=row["COUNTRY_CODE"],
                    charting_type_desc=row["CHARTING_TYPE_DESC"],
                )
                self.fix_chrt.append(record)

    def parse_fix_nav(self) -> None:
        file_path = path.join(self.__dir_path, FIX_NAV_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {FIX_NAV_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = FIX_NAV(
                    eff_date=row["EFF_DATE"],
                    fix_id=row["FIX_ID"],
                    icao_region_code=row["ICAO_REGION_CODE"],
                    state_code=row["STATE_CODE"],
                    country_code=row["COUNTRY_CODE"],
                    nav_id=row["NAV_ID"],
                    nav_type=row["NAV_TYPE"],
                    bearing=row["BEARING"],
                    distance=row["DISTANCE"],
                )
                self.fix_nav.append(record)

    def to_dict(self) -> dict:
        return {
            **self.fix_base_to_dict(),
            **self.fix_chrt_to_dict(),
            **self.fix_nav_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.fix_base_to_db(db_cursor)
        self.fix_chrt_to_db(db_cursor)
        self.fix_nav_to_db(db_cursor)

    def fix_base_to_dict(self) -> dict:
        return {"fix_base": [item.to_dict() for item in self.fix_base]}

    def fix_chrt_to_dict(self) -> dict:
        return {"fix_chrt": [item.to_dict() for item in self.fix_chrt]}

    def fix_nav_to_dict(self) -> dict:
        return {"fix_nav": [item.to_dict() for item in self.fix_nav]}

    def fix_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.fix_base) > 0:
            print(f"               Processing {FIX_BASE_FILE_NAME}")
            process_table(db_cursor, self.fix_base)

    def fix_chrt_to_db(self, db_cursor: Cursor) -> None:
        if len(self.fix_chrt) > 0:
            print(f"               Processing {FIX_CHRT_FILE_NAME}")
            process_table(db_cursor, self.fix_chrt)

    def fix_nav_to_db(self, db_cursor: Cursor) -> None:
        if len(self.fix_nav) > 0:
            print(f"               Processing {FIX_NAV_FILE_NAME}")
            process_table(db_cursor, self.fix_nav)
