from nasrparse.records.arb import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.arb import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class ARBs:
    __dir_path: str

    arb_base: list[ARB_BASE]
    arb_seg: list[ARB_SEG]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.arb_base = []
        self.arb_seg = []

    def parse(self) -> None:
        self.parse_arb_base()
        self.parse_arb_seg()

    def parse_arb_base(self) -> None:
        file_path = path.join(self.__dir_path, ARB_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {ARB_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = ARB_BASE(
                    eff_date=row["EFF_DATE"],
                    location_id=row["LOCATION_ID"],
                    location_name=row["LOCATION_NAME"],
                    computer_id=row["COMPUTER_ID"],
                    icao_id=row["ICAO_ID"],
                    location_type=row["LOCATION_TYPE"],
                    city=row["CITY"],
                    state=row["STATE"],
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
                    cross_ref=row["CROSS_REF"],
                )
                self.arb_base.append(record)

    def parse_arb_seg(self) -> None:
        file_path = path.join(self.__dir_path, ARB_SEG_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {ARB_SEG_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = ARB_SEG(
                    eff_date=row["EFF_DATE"],
                    location_id=row["LOCATION_ID"],
                    location_name=row["LOCATION_NAME"],
                    rec_id=row["REC_ID"],
                    altitude=row["ALTITUDE"],
                    type=row["TYPE"],
                    point_seq=row["POINT_SEQ"],
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
                    bndry_pt_descrip=row["BNDRY_PT_DESCRIP"],
                    nas_descrip_flag=row["NAS_DESCRIP_FLAG"],
                )
                self.arb_seg.append(record)

    def to_dict(self) -> dict:
        return {
            **self.arb_base_to_dict(),
            **self.arb_seg_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.arb_base_to_db(db_cursor)
        self.arb_seg_to_db(db_cursor)

    def arb_base_to_dict(self) -> dict:
        return {"arb_base": [item.to_dict() for item in self.arb_base]}

    def arb_seg_to_dict(self) -> dict:
        return {"arb_seg": [item.to_dict() for item in self.arb_seg]}

    def arb_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.arb_base) > 0:
            print(f"               Processing {ARB_BASE_FILE_NAME}")
            process_table(db_cursor, self.arb_base)

    def arb_seg_to_db(self, db_cursor: Cursor) -> None:
        if len(self.arb_seg) > 0:
            print(f"               Processing {ARB_SEG_FILE_NAME}")
            process_table(db_cursor, self.arb_seg)
