from nasrparse.records.awos import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.awos import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class AWOSs:
    __dir_path: str

    awos_base: list[AWOS_BASE]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.awos_base = []

    def parse(self) -> None:
        self.parse_awos_base()

    def parse_awos_base(self) -> None:
        file_path = path.join(self.__dir_path, AWOS_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {AWOS_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = AWOS_BASE(
                    eff_date=row["EFF_DATE"],
                    asos_awos_id=row["ASOS_AWOS_ID"],
                    asos_awos_type=row["ASOS_AWOS_TYPE"],
                    state_code=row["STATE_CODE"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    commissioned_date=row["COMMISSIONED_DATE"],
                    navaid_flag=row["NAVAID_FLAG"],
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
                    elev=row["ELEV"],
                    survey_method_code=row["SURVEY_METHOD_CODE"],
                    phone_no=row["PHONE_NO"],
                    second_phone_no=row["SECOND_PHONE_NO"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    remark=row["REMARK"],
                )
                self.awos_base.append(record)

    def to_dict(self) -> dict:
        return {
            **self.awos_base_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.awos_base_to_db(db_cursor)

    def awos_base_to_dict(self) -> dict:
        return {"awos_base": [item.to_dict() for item in self.awos_base]}

    def awos_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.awos_base) > 0:
            print(f"               Processing {AWOS_FILE_NAME}")
            process_table(db_cursor, self.awos_base)
