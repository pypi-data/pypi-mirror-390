from nasrparse.records.pja import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.pja import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class PJAs:
    __dir_path: str

    pja_base: list[PJA_BASE]
    pja_con: list[PJA_CON]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.pja_base = []
        self.pja_con = []

    def parse(self) -> None:
        self.parse_pja_base()
        self.parse_pja_con()

    def parse_pja_base(self) -> None:
        file_path = path.join(self.__dir_path, PJA_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {PJA_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = PJA_BASE(
                    eff_date=row["EFF_DATE"],
                    pja_id=row["PJA_ID"],
                    nav_id=row["NAV_ID"],
                    nav_type=row["NAV_TYPE"],
                    radial=row["RADIAL"],
                    distance=row["DISTANCE"],
                    navaid_name=row["NAVAID_NAME"],
                    state_code=row["STATE_CODE"],
                    city=row["CITY"],
                    latitude=row["LATITUDE"],
                    lat_decimal=row["LAT_DECIMAL"],
                    longitude=row["LONGITUDE"],
                    long_decimal=row["LONG_DECIMAL"],
                    arpt_id=row["ARPT_ID"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    drop_zone_name=row["DROP_ZONE_NAME"],
                    max_altitude=row["MAX_ALTITUDE"],
                    max_altitude_type_code=row["MAX_ALTITUDE_TYPE_CODE"],
                    pja_radius=row["PJA_RADIUS"],
                    chart_request_flag=row["CHART_REQUEST_FLAG"],
                    publish_criteria=row["PUBLISH_CRITERIA"],
                    description=row["DESCRIPTION"],
                    time_of_use=row["TIME_OF_USE"],
                    fss_id=row["FSS_ID"],
                    fss_name=row["FSS_NAME"],
                    pja_use=row["PJA_USE"],
                    volume=row["VOLUME"],
                    pja_user=row["PJA_USER"],
                    remark=row["REMARK"],
                )
                self.pja_base.append(record)

    def parse_pja_con(self) -> None:
        file_path = path.join(self.__dir_path, PJA_CON_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {PJA_CON_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = PJA_CON(
                    eff_date=row["EFF_DATE"],
                    pja_id=row["PJA_ID"],
                    fac_id=row["FAC_ID"],
                    fac_name=row["FAC_NAME"],
                    loc_id=row["LOC_ID"],
                    commercial_freq=row["COMMERCIAL_FREQ"],
                    commercial_chart_flag=row["COMMERCIAL_CHART_FLAG"],
                    mil_freq=row["MIL_FREQ"],
                    mil_chart_flag=row["MIL_CHART_FLAG"],
                    sector=row["SECTOR"],
                    contact_freq_altitude=row["CONTACT_FREQ_ALTITUDE"],
                )
                self.pja_con.append(record)

    def to_dict(self) -> dict:
        return {
            **self.pja_base_to_dict(),
            **self.pja_con_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.pja_base_to_db(db_cursor)
        self.pja_con_to_db(db_cursor)

    def pja_base_to_dict(self) -> dict:
        return {"pja_base": [item.to_dict() for item in self.pja_base]}

    def pja_con_to_dict(self) -> dict:
        return {"pja_con": [item.to_dict() for item in self.pja_con]}

    def pja_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.pja_base) > 0:
            print(f"               Processing {PJA_BASE_FILE_NAME}")
            process_table(db_cursor, self.pja_base)

    def pja_con_to_db(self, db_cursor: Cursor) -> None:
        if len(self.pja_con) > 0:
            print(f"               Processing {PJA_CON_FILE_NAME}")
            process_table(db_cursor, self.pja_con)
