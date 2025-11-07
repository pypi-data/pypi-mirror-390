from nasrparse.records.hpf import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.hpf import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class HPFs:
    __dir_path: str

    hpf_base: list[HPF_BASE]
    hpf_chrt: list[HPF_CHRT]
    hpf_rmk: list[HPF_RMK]
    hpf_spd_alt: list[HPF_SPD_ALT]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.hpf_base = []
        self.hpf_chrt = []
        self.hpf_rmk = []
        self.hpf_spd_alt = []

    def parse(self) -> None:
        self.parse_hpf_base()
        self.parse_hpf_chrt()
        self.parse_hpf_rmk()
        self.parse_hpf_spd_alt()

    def parse_hpf_base(self) -> None:
        file_path = path.join(self.__dir_path, HPF_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {HPF_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = HPF_BASE(
                    eff_date=row["EFF_DATE"],
                    hp_name=row["HP_NAME"],
                    hp_no=row["HP_NO"],
                    state_code=row["STATE_CODE"],
                    country_code=row["COUNTRY_CODE"],
                    fix_id=row["FIX_ID"],
                    icao_region_code=row["ICAO_REGION_CODE"],
                    nav_id=row["NAV_ID"],
                    nav_type=row["NAV_TYPE"],
                    hold_direction=row["HOLD_DIRECTION"],
                    hold_deg_or_crs=row["HOLD_DEG_OR_CRS"],
                    azimuth=row["AZIMUTH"],
                    course_inbound_deg=row["COURSE_INBOUND_DEG"],
                    turn_direction=row["TURN_DIRECTION"],
                    leg_length_dist=row["LEG_LENGTH_DIST"],
                )
                self.hpf_base.append(record)

    def parse_hpf_chrt(self) -> None:
        file_path = path.join(self.__dir_path, HPF_CHRT_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {HPF_CHRT_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = HPF_CHRT(
                    eff_date=row["EFF_DATE"],
                    hp_name=row["HP_NAME"],
                    hp_no=row["HP_NO"],
                    state_code=row["STATE_CODE"],
                    country_code=row["COUNTRY_CODE"],
                    charting_type_desc=row["CHARTING_TYPE_DESC"],
                )
                self.hpf_chrt.append(record)

    def parse_hpf_rmk(self) -> None:
        file_path = path.join(self.__dir_path, HPF_RMK_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {HPF_RMK_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = HPF_RMK(
                    eff_date=row["EFF_DATE"],
                    hp_name=row["HP_NAME"],
                    hp_no=row["HP_NO"],
                    state_code=row["STATE_CODE"],
                    country_code=row["COUNTRY_CODE"],
                    tab_name=row["TAB_NAME"],
                    ref_col_name=row["REF_COL_NAME"],
                    ref_col_seq_no=row["REF_COL_SEQ_NO"],
                    remark=row["REMARK"],
                )
                self.hpf_rmk.append(record)

    def parse_hpf_spd_alt(self) -> None:
        file_path = path.join(self.__dir_path, HPF_SPD_ALT_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {HPF_SPD_ALT_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = HPF_SPD_ALT(
                    eff_date=row["EFF_DATE"],
                    hp_name=row["HP_NAME"],
                    hp_no=row["HP_NO"],
                    state_code=row["STATE_CODE"],
                    country_code=row["COUNTRY_CODE"],
                    speed_range=row["SPEED_RANGE"],
                    altitude=row["ALTITUDE"],
                )
                self.hpf_spd_alt.append(record)

    def to_dict(self) -> dict:
        return {
            **self.hpf_base_to_dict(),
            **self.hpf_chrt_to_dict(),
            **self.hpf_rmk_to_dict(),
            **self.hpf_spd_alt_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.hpf_base_to_db(db_cursor)
        self.hpf_chrt_to_db(db_cursor)
        self.hpf_rmk_to_db(db_cursor)
        self.hpf_spd_alt_to_db(db_cursor)

    def hpf_base_to_dict(self) -> dict:
        return {"hpf_base": [item.to_dict() for item in self.hpf_base]}

    def hpf_chrt_to_dict(self) -> dict:
        return {"hpf_chrt": [item.to_dict() for item in self.hpf_chrt]}

    def hpf_rmk_to_dict(self) -> dict:
        return {"hpf_rmk": [item.to_dict() for item in self.hpf_rmk]}

    def hpf_spd_alt_to_dict(self) -> dict:
        return {"hpf_spd_alt": [item.to_dict() for item in self.hpf_spd_alt]}

    def hpf_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.hpf_base) > 0:
            print(f"               Processing {HPF_BASE_FILE_NAME}")
            process_table(db_cursor, self.hpf_base)

    def hpf_chrt_to_db(self, db_cursor: Cursor) -> None:
        if len(self.hpf_chrt) > 0:
            print(f"               Processing {HPF_CHRT_FILE_NAME}")
            process_table(db_cursor, self.hpf_chrt)

    def hpf_rmk_to_db(self, db_cursor: Cursor) -> None:
        if len(self.hpf_rmk) > 0:
            print(f"               Processing {HPF_RMK_FILE_NAME}")
            process_table(db_cursor, self.hpf_rmk)

    def hpf_spd_alt_to_db(self, db_cursor: Cursor) -> None:
        if len(self.hpf_spd_alt) > 0:
            print(f"               Processing {HPF_SPD_ALT_FILE_NAME}")
            process_table(db_cursor, self.hpf_spd_alt)
