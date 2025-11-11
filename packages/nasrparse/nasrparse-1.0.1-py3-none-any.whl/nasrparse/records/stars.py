from nasrparse.records.star import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.star import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class STARs:
    __dir_path: str

    star_apt: list[STAR_APT]
    star_base: list[STAR_BASE]
    star_rte: list[STAR_RTE]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.star_apt = []
        self.star_base = []
        self.star_rte = []

    def parse(self) -> None:
        self.parse_star_apt()
        self.parse_star_base()
        self.parse_star_rte()

    def parse_star_apt(self) -> None:
        file_path = path.join(self.__dir_path, STAR_APT_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {STAR_APT_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = STAR_APT(
                    eff_date=row["EFF_DATE"],
                    star_computer_code=row["STAR_COMPUTER_CODE"],
                    artcc=row["ARTCC"],
                    body_name=row["BODY_NAME"],
                    body_seq=row["BODY_SEQ"],
                    arpt_id=row["ARPT_ID"],
                    rwy_end_id=row["RWY_END_ID"],
                )
                self.star_apt.append(record)

    def parse_star_base(self) -> None:
        file_path = path.join(self.__dir_path, STAR_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {STAR_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = STAR_BASE(
                    eff_date=row["EFF_DATE"],
                    star_computer_code=row["STAR_COMPUTER_CODE"],
                    artcc=row["ARTCC"],
                    arrival_name=row["ARRIVAL_NAME"],
                    amendment_no=row["AMENDMENT_NO"],
                    star_amend_eff_date=row["STAR_AMEND_EFF_DATE"],
                    rnav_flag=row["RNAV_FLAG"],
                    served_arpt=row["SERVED_ARPT"],
                )
                self.star_base.append(record)

    def parse_star_rte(self) -> None:
        file_path = path.join(self.__dir_path, STAR_RTE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {STAR_RTE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = STAR_RTE(
                    eff_date=row["EFF_DATE"],
                    star_computer_code=row["STAR_COMPUTER_CODE"],
                    artcc=row["ARTCC"],
                    route_portion_type=row["ROUTE_PORTION_TYPE"],
                    route_name=row["ROUTE_NAME"],
                    body_seq=row["BODY_SEQ"],
                    transition_computer_code=row["TRANSITION_COMPUTER_CODE"],
                    point_seq=row["POINT_SEQ"],
                    point=row["POINT"],
                    icao_region_code=row["ICAO_REGION_CODE"],
                    point_type=row["POINT_TYPE"],
                    next_point=row["NEXT_POINT"],
                    arpt_rwy_assoc=row["ARPT_RWY_ASSOC"],
                )
                self.star_rte.append(record)

    def to_dict(self) -> dict:
        return {
            **self.star_apt_to_dict(),
            **self.star_base_to_dict(),
            **self.star_rte_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.star_apt_to_db(db_cursor)
        self.star_base_to_db(db_cursor)
        self.star_rte_to_db(db_cursor)

    def star_apt_to_dict(self) -> dict:
        return {"star_apt": [item.to_dict() for item in self.star_apt]}

    def star_base_to_dict(self) -> dict:
        return {"star_base": [item.to_dict() for item in self.star_base]}

    def star_rte_to_dict(self) -> dict:
        return {"star_rte": [item.to_dict() for item in self.star_rte]}

    def star_apt_to_db(self, db_cursor: Cursor) -> None:
        if len(self.star_apt) > 0:
            print(f"               Processing {STAR_APT_FILE_NAME}")
            process_table(db_cursor, self.star_apt)

    def star_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.star_base) > 0:
            print(f"               Processing {STAR_BASE_FILE_NAME}")
            process_table(db_cursor, self.star_base)

    def star_rte_to_db(self, db_cursor: Cursor) -> None:
        if len(self.star_rte) > 0:
            print(f"               Processing {STAR_RTE_FILE_NAME}")
            process_table(db_cursor, self.star_rte)
