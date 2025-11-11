from nasrparse.records.mil import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.mil import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class MILs:
    __dir_path: str

    mil_base: list[MIL_BASE]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.mil_base = []

    def parse(self) -> None:
        self.parse_mil_base()

    def parse_mil_base(self) -> None:
        file_path = path.join(self.__dir_path, MIL_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MIL_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MIL_BASE(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    state_code=row["STATE_CODE"],
                    arpt_id=row["ARPT_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    mil_ops_oper_code=row["MIL_OPS_OPER_CODE"],
                    mil_ops_call=row["MIL_OPS_CALL"],
                    mil_ops_hrs=row["MIL_OPS_HRS"],
                    amcp_hrs=row["AMCP_HRS"],
                    pmsv_hrs=row["PMSV_HRS"],
                    remark=row["REMARK"],
                )
                self.mil_base.append(record)

    def to_dict(self) -> dict:
        return {
            **self.mil_base_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.mil_base_to_db(db_cursor)

    def mil_base_to_dict(self) -> dict:
        return {"mil_base": [item.to_dict() for item in self.mil_base]}

    def mil_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.mil_base) > 0:
            print(f"               Processing {MIL_FILE_NAME}")
            process_table(db_cursor, self.mil_base)
