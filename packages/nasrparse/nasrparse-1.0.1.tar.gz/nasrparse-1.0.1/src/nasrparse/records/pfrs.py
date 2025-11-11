from nasrparse.records.pfr import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.pfr import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class PFRs:
    __dir_path: str

    pfr_base: list[PFR_BASE]
    pfr_rmt_fmt: list[PFR_RMT_FMT]
    pfr_seg: list[PFR_SEG]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.pfr_base = []
        self.pfr_rmt_fmt = []
        self.pfr_seg = []

    def parse(self) -> None:
        self.parse_pfr_base()
        self.parse_pfr_rmt_fmt()
        self.parse_pfr_seg()

    def parse_pfr_base(self) -> None:
        file_path = path.join(self.__dir_path, PFR_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {PFR_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = PFR_BASE(
                    eff_date=row["EFF_DATE"],
                    origin_id=row["ORIGIN_ID"],
                    dstn_id=row["DSTN_ID"],
                    pfr_type_code=row["PFR_TYPE_CODE"],
                    route_no=row["ROUTE_NO"],
                    origin_city=row["ORIGIN_CITY"],
                    origin_state_code=row["ORIGIN_STATE_CODE"],
                    origin_country_code=row["ORIGIN_COUNTRY_CODE"],
                    dstn_city=row["DSTN_CITY"],
                    dstn_state_code=row["DSTN_STATE_CODE"],
                    dstn_country_code=row["DSTN_COUNTRY_CODE"],
                    special_area_descrip=row["SPECIAL_AREA_DESCRIP"],
                    alt_descrip=row["ALT_DESCRIP"],
                    aircraft=row["AIRCRAFT"],
                    hours=row["HOURS"],
                    route_dir_descrip=row["ROUTE_DIR_DESCRIP"],
                    designator=row["DESIGNATOR"],
                    nar_type=row["NAR_TYPE"],
                    inland_fac_fix=row["INLAND_FAC_FIX"],
                    coastal_fix=row["COASTAL_FIX"],
                    destination=row["DESTINATION"],
                    route_string=row["ROUTE_STRING"],
                )
                self.pfr_base.append(record)

    def parse_pfr_rmt_fmt(self) -> None:
        file_path = path.join(self.__dir_path, PFR_RMT_FMT_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {PFR_RMT_FMT_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = PFR_RMT_FMT(
                    orig=row["Orig"],
                    route_string=row["Route String"],
                    dest=row["Dest"],
                    hours1=row["Hours1"],
                    type=row["Type"],
                    area=row["Area"],
                    altitude=row["Altitude"],
                    aircraft=row["Aircraft"],
                    direction=row["Direction"],
                    seq=row["Seq"],
                    dcntr=row["DCNTR"],
                    acntr=row["ACNTR"],
                )
                self.pfr_rmt_fmt.append(record)

    def parse_pfr_seg(self) -> None:
        file_path = path.join(self.__dir_path, PFR_SEG_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {PFR_SEG_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = PFR_SEG(
                    eff_date=row["EFF_DATE"],
                    origin_id=row["ORIGIN_ID"],
                    dstn_id=row["DSTN_ID"],
                    pfr_type_code=row["PFR_TYPE_CODE"],
                    route_no=row["ROUTE_NO"],
                    segment_seq=row["SEGMENT_SEQ"],
                    seg_value=row["SEG_VALUE"],
                    seg_type=row["SEG_TYPE"],
                    state_code=row["STATE_CODE"],
                    country_code=row["COUNTRY_CODE"],
                    icao_region_code=row["ICAO_REGION_CODE"],
                    nav_type=row["NAV_TYPE"],
                    next_seg=row["NEXT_SEG"],
                )
                self.pfr_seg.append(record)

    def to_dict(self) -> dict:
        return {
            **self.pfr_base_to_dict(),
            **self.pfr_rmt_fmt_to_dict(),
            **self.pfr_seg_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.pfr_base_to_db(db_cursor)
        self.pfr_rmt_fmt_to_db(db_cursor)
        self.pfr_seg_to_db(db_cursor)

    def pfr_base_to_dict(self) -> dict:
        return {"pfr_base": [item.to_dict() for item in self.pfr_base]}

    def pfr_rmt_fmt_to_dict(self) -> dict:
        return {"pfr_rmt_fmt": [item.to_dict() for item in self.pfr_rmt_fmt]}

    def pfr_seg_to_dict(self) -> dict:
        return {"pfr_seg": [item.to_dict() for item in self.pfr_seg]}

    def pfr_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.pfr_base) > 0:
            print(f"               Processing {PFR_BASE_FILE_NAME}")
            process_table(db_cursor, self.pfr_base)

    def pfr_rmt_fmt_to_db(self, db_cursor: Cursor) -> None:
        if len(self.pfr_rmt_fmt) > 0:
            print(f"               Processing {PFR_RMT_FMT_FILE_NAME}")
            process_table(db_cursor, self.pfr_rmt_fmt)

    def pfr_seg_to_db(self, db_cursor: Cursor) -> None:
        if len(self.pfr_seg) > 0:
            print(f"               Processing {PFR_SEG_FILE_NAME}")
            process_table(db_cursor, self.pfr_seg)
