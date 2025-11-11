from nasrparse.records.dp import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.dp import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class DPs:
    __dir_path: str

    dp_apt: list[DP_APT]
    dp_base: list[DP_BASE]
    dp_rte: list[DP_RTE]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.dp_apt = []
        self.dp_base = []
        self.dp_rte = []

    def parse(self) -> None:
        self.parse_dp_apt()
        self.parse_dp_base()
        self.parse_dp_rte()

    def parse_dp_apt(self) -> None:
        file_path = path.join(self.__dir_path, DP_APT_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {DP_APT_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = DP_APT(
                    eff_date=row["EFF_DATE"],
                    dp_computer_code=row["DP_COMPUTER_CODE"],
                    dp_name=row["DP_NAME"],
                    artcc=row["ARTCC"],
                    body_name=row["BODY_NAME"],
                    body_seq=row["BODY_SEQ"],
                    arpt_id=row["ARPT_ID"],
                    rwy_end_id=row["RWY_END_ID"],
                )
                self.dp_apt.append(record)

    def parse_dp_base(self) -> None:
        file_path = path.join(self.__dir_path, DP_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {DP_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = DP_BASE(
                    eff_date=row["EFF_DATE"],
                    dp_computer_code=row["DP_COMPUTER_CODE"],
                    dp_name=row["DP_NAME"],
                    artcc=row["ARTCC"],
                    amendment_no=row["AMENDMENT_NO"],
                    dp_amend_eff_date=row["DP_AMEND_EFF_DATE"],
                    rnav_flag=row["RNAV_FLAG"],
                    graphical_dp_type=row["GRAPHICAL_DP_TYPE"],
                    served_arpt=row["SERVED_ARPT"],
                )
                self.dp_base.append(record)

    def parse_dp_rte(self) -> None:
        file_path = path.join(self.__dir_path, DP_RTE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {DP_RTE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = DP_RTE(
                    eff_date=row["EFF_DATE"],
                    dp_computer_code=row["DP_COMPUTER_CODE"],
                    dp_name=row["DP_NAME"],
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
                self.dp_rte.append(record)

    def to_dict(self) -> dict:
        return {
            **self.dp_apt_to_dict(),
            **self.dp_base_to_dict(),
            **self.dp_rte_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.dp_apt_to_db(db_cursor)
        self.dp_base_to_db(db_cursor)
        self.dp_rte_to_db(db_cursor)

    def dp_apt_to_dict(self) -> dict:
        return {"dp_apt": [item.to_dict() for item in self.dp_apt]}

    def dp_base_to_dict(self) -> dict:
        return {"dp_base": [item.to_dict() for item in self.dp_base]}

    def dp_rte_to_dict(self) -> dict:
        return {"dp_rte": [item.to_dict() for item in self.dp_rte]}

    def dp_apt_to_db(self, db_cursor: Cursor) -> None:
        if len(self.dp_apt) > 0:
            print(f"               Processing {DP_APT_FILE_NAME}")
            process_table(db_cursor, self.dp_apt)

    def dp_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.dp_base) > 0:
            print(f"               Processing {DP_BASE_FILE_NAME}")
            process_table(db_cursor, self.dp_base)

    def dp_rte_to_db(self, db_cursor: Cursor) -> None:
        if len(self.dp_rte) > 0:
            print(f"               Processing {DP_RTE_FILE_NAME}")
            process_table(db_cursor, self.dp_rte)
