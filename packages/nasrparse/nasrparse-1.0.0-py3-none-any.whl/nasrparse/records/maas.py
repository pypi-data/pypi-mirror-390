from nasrparse.records.maa import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.maa import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class MAAs:
    __dir_path: str

    maa_base: list[MAA_BASE]
    maa_con: list[MAA_CON]
    maa_rmk: list[MAA_RMK]
    maa_shp: list[MAA_SHP]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.maa_base = []
        self.maa_con = []
        self.maa_rmk = []
        self.maa_shp = []

    def parse(self) -> None:
        self.parse_maa_base()
        self.parse_maa_con()
        self.parse_maa_rmk()
        self.parse_maa_shp()

    def parse_maa_base(self) -> None:
        file_path = path.join(self.__dir_path, MAA_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MAA_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MAA_BASE(
                    eff_date=row["EFF_DATE"],
                    maa_id=row["MAA_ID"],
                    maa_type_name=row["MAA_TYPE_NAME"],
                    nav_id=row["NAV_ID"],
                    nav_type=row["NAV_TYPE"],
                    nav_radial=row["NAV_RADIAL"],
                    nav_distance=row["NAV_DISTANCE"],
                    state_code=row["STATE_CODE"],
                    city=row["CITY"],
                    latitude=row["LATITUDE"],
                    longitude=row["LONGITUDE"],
                    arpt_ids=row["ARPT_IDS"],
                    nearest_arpt=row["NEAREST_ARPT"],
                    nearest_arpt_dist=row["NEAREST_ARPT_DIST"],
                    nearest_arpt_dir=row["NEAREST_ARPT_DIR"],
                    maa_name=row["MAA_NAME"],
                    max_alt=row["MAX_ALT"],
                    min_alt=row["MIN_ALT"],
                    maa_radius=row["MAA_RADIUS"],
                    description=row["DESCRIPTION"],
                    maa_use=row["MAA_USE"],
                    check_notams=row["CHECK_NOTAMS"],
                    time_of_use=row["TIME_OF_USE"],
                    user_group_name=row["USER_GROUP_NAME"],
                )
                self.maa_base.append(record)

    def parse_maa_con(self) -> None:
        file_path = path.join(self.__dir_path, MAA_CON_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MAA_CON_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MAA_CON(
                    eff_date=row["EFF_DATE"],
                    maa_id=row["MAA_ID"],
                    freq_seq=row["FREQ_SEQ"],
                    fac_id=row["FAC_ID"],
                    fac_name=row["FAC_NAME"],
                    commercial_freq=row["COMMERCIAL_FREQ"],
                    commercial_chart_flag=row["COMMERCIAL_CHART_FLAG"],
                    mil_freq=row["MIL_FREQ"],
                    mil_chart_flag=row["MIL_CHART_FLAG"],
                )
                self.maa_con.append(record)

    def parse_maa_rmk(self) -> None:
        file_path = path.join(self.__dir_path, MAA_RMK_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MAA_RMK_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MAA_RMK(
                    eff_date=row["EFF_DATE"],
                    maa_id=row["MAA_ID"],
                    tab_name=row["TAB_NAME"],
                    ref_col_name=row["REF_COL_NAME"],
                    ref_col_seq_no=row["REF_COL_SEQ_NO"],
                    remark=row["REMARK"],
                )
                self.maa_rmk.append(record)

    def parse_maa_shp(self) -> None:
        file_path = path.join(self.__dir_path, MAA_SHP_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MAA_SHP_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MAA_SHP(
                    eff_date=row["EFF_DATE"],
                    maa_id=row["MAA_ID"],
                    point_seq=row["POINT_SEQ"],
                    latitude=row["LATITUDE"],
                    longitude=row["LONGITUDE"],
                )
                self.maa_shp.append(record)

    def to_dict(self) -> dict:
        return {
            **self.maa_base_to_dict(),
            **self.maa_con_to_dict(),
            **self.maa_rmk_to_dict(),
            **self.maa_shp_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.maa_base_to_db(db_cursor)
        self.maa_con_to_db(db_cursor)
        self.maa_rmk_to_db(db_cursor)
        self.maa_shp_to_db(db_cursor)

    def maa_base_to_dict(self) -> dict:
        return {"maa_base": [item.to_dict() for item in self.maa_base]}

    def maa_con_to_dict(self) -> dict:
        return {"maa_con": [item.to_dict() for item in self.maa_con]}

    def maa_rmk_to_dict(self) -> dict:
        return {"maa_rmk": [item.to_dict() for item in self.maa_rmk]}

    def maa_shp_to_dict(self) -> dict:
        return {"maa_shp": [item.to_dict() for item in self.maa_shp]}

    def maa_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.maa_base) > 0:
            print(f"               Processing {MAA_BASE_FILE_NAME}")
            process_table(db_cursor, self.maa_base)

    def maa_con_to_db(self, db_cursor: Cursor) -> None:
        if len(self.maa_con) > 0:
            print(f"               Processing {MAA_CON_FILE_NAME}")
            process_table(db_cursor, self.maa_con)

    def maa_rmk_to_db(self, db_cursor: Cursor) -> None:
        if len(self.maa_rmk) > 0:
            print(f"               Processing {MAA_RMK_FILE_NAME}")
            process_table(db_cursor, self.maa_rmk)

    def maa_shp_to_db(self, db_cursor: Cursor) -> None:
        if len(self.maa_shp) > 0:
            print(f"               Processing {MAA_SHP_FILE_NAME}")
            process_table(db_cursor, self.maa_shp)
