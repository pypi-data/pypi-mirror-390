from nasrparse.records.lid import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.lid import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class LIDs:
    __dir_path: str

    lid_base: list[LID_BASE]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.lid_base = []

    def parse(self) -> None:
        self.parse_lid_base()

    def parse_lid_base(self) -> None:
        file_path = path.join(self.__dir_path, LID_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {LID_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = LID_BASE(
                    eff_date=row["EFF_DATE"],
                    country_code=row["COUNTRY_CODE"],
                    loc_id=row["LOC_ID"],
                    region_code=row["REGION_CODE"],
                    state_code=row["STATE"],
                    city=row["CITY"],
                    lid_group=row["LID_GROUP"],
                    fac_type=row["FAC_TYPE"],
                    fac_name=row["FAC_NAME"],
                    resp_artcc_id=row["RESP_ARTCC_ID"],
                    artcc_computer_id=row["ARTCC_COMPUTER_ID"],
                    fss_id=row["FSS_ID"],
                )
                self.lid_base.append(record)

    def to_dict(self) -> dict:
        return {
            **self.lid_base_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.lid_base_to_db(db_cursor)

    def lid_base_to_dict(self) -> dict:
        return {"lid_base": [item.to_dict() for item in self.lid_base]}

    def lid_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.lid_base) > 0:
            print(f"               Processing {LID_FILE_NAME}")
            process_table(db_cursor, self.lid_base)
