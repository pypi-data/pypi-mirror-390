from nasrparse.records.fss import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.fss import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class FSSs:
    __dir_path: str

    fss_base: list[FSS_BASE]
    fss_rmk: list[FSS_RMK]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.fss_base = []
        self.fss_rmk = []

    def parse(self) -> None:
        self.parse_fss_base()
        self.parse_fss_rmk()

    def parse_fss_base(self) -> None:
        file_path = path.join(self.__dir_path, FSS_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {FSS_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = FSS_BASE(
                    eff_date=row["EFF_DATE"],
                    fss_id=row["FSS_ID"],
                    name=row["NAME"],
                    city=row["CITY"],
                    state_code=row["STATE_CODE"],
                    country_code=row["COUNTRY_CODE"],
                    update_date=row["UPDATE_DATE"],
                    fss_fac_type=row["FSS_FAC_TYPE"],
                    voice_call=row["VOICE_CALL"],
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
                    opr_hours=row["OPR_HOURS"],
                    fac_status=row["FAC_STATUS"],
                    alternate_fss=row["ALTERNATE_FSS"],
                    wea_radar_flag=row["WEA_RADAR_FLAG"],
                    phone_no=row["PHONE_NO"],
                    toll_free_no=row["TOLL_FREE_NO"],
                )
                self.fss_base.append(record)

    def parse_fss_rmk(self) -> None:
        file_path = path.join(self.__dir_path, FSS_RMK_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {FSS_RMK_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = FSS_RMK(
                    eff_date=row["EFF_DATE"],
                    fss_id=row["FSS_ID"],
                    name=row["NAME"],
                    city=row["CITY"],
                    state_code=row["STATE_CODE"],
                    country_code=row["COUNTRY_CODE"],
                    ref_col_name=row["REF_COL_NAME"],
                    ref_col_seq_no=row["REF_COL_SEQ_NO"],
                    remark=row["REMARK"],
                )
                self.fss_rmk.append(record)

    def to_dict(self) -> dict:
        return {
            **self.fss_base_to_dict(),
            **self.fss_rmk_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.fss_base_to_db(db_cursor)
        self.fss_rmk_to_db(db_cursor)

    def fss_base_to_dict(self) -> dict:
        return {"fss_base": [item.to_dict() for item in self.fss_base]}

    def fss_rmk_to_dict(self) -> dict:
        return {"fss_rmk": [item.to_dict() for item in self.fss_rmk]}

    def fss_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.fss_base) > 0:
            print(f"               Processing {FSS_BASE_FILE_NAME}")
            process_table(db_cursor, self.fss_base)

    def fss_rmk_to_db(self, db_cursor: Cursor) -> None:
        if len(self.fss_rmk) > 0:
            print(f"               Processing {FSS_RMK_FILE_NAME}")
            process_table(db_cursor, self.fss_rmk)
