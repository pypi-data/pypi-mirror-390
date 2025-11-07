from nasrparse.records.rdr import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.rdr import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class RDRs:
    __dir_path: str

    rdr_base: list[RDR_BASE]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.rdr_base = []

    def parse(self) -> None:
        self.parse_rdr_base()

    def parse_rdr_base(self) -> None:
        file_path = path.join(self.__dir_path, RDR_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {RDR_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = RDR_BASE(
                    eff_date=row["EFF_DATE"],
                    facility_id=row["FACILITY_ID"],
                    facility_type=row["FACILITY_TYPE"],
                    state_code=row["STATE_CODE"],
                    country_code=row["COUNTRY_CODE"],
                    radar_type=row["RADAR_TYPE"],
                    radar_no=row["RADAR_NO"],
                    radar_hrs=row["RADAR_HRS"],
                    remark=row["REMARK"],
                )
                self.rdr_base.append(record)

    def to_dict(self) -> dict:
        return {
            **self.rdr_base_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.rdr_base_to_db(db_cursor)

    def rdr_base_to_dict(self) -> dict:
        return {"rdr_base": [item.to_dict() for item in self.rdr_base]}

    def rdr_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.rdr_base) > 0:
            print(f"               Processing {RDR_FILE_NAME}")
            process_table(db_cursor, self.rdr_base)
