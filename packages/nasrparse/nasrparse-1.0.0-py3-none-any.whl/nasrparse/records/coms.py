from nasrparse.records.com import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.com import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class COMs:
    __dir_path: str

    com_base: list[COM_BASE]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.com_base = []

    def parse(self) -> None:
        self.parse_com_base()

    def parse_com_base(self) -> None:
        file_path = path.join(self.__dir_path, COM_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {COM_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = COM_BASE(
                    eff_date=row["EFF_DATE"],
                    comm_loc_id=row["COMM_LOC_ID"],
                    comm_type=row["COMM_TYPE"],
                    nav_id=row["NAV_ID"],
                    nav_type=row["NAV_TYPE"],
                    city=row["CITY"],
                    state_code=row["STATE_CODE"],
                    region_code=row["REGION_CODE"],
                    country_code=row["COUNTRY_CODE"],
                    comm_outlet_name=row["COMM_OUTLET_NAME"],
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
                    facility_id=row["FACILITY_ID"],
                    alt_fss_id=row["ALT_FSS_ID"],
                    alt_fss_name=row["ALT_FSS_NAME"],
                    opr_hrs=row["OPR_HRS"],
                    comm_status_code=row["COMM_STATUS_CODE"],
                    comm_status_date=row["COMM_STATUS_DATE"],
                    remark=row["REMARK"],
                )
                self.com_base.append(record)

    def to_dict(self) -> dict:
        return {
            **self.com_base_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.com_base_to_db(db_cursor)

    def com_base_to_dict(self) -> dict:
        return {"com_base": [item.to_dict() for item in self.com_base]}

    def com_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.com_base) > 0:
            print(f"               Processing {COM_FILE_NAME}")
            process_table(db_cursor, self.com_base)
