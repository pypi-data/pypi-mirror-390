from nasrparse.records.atc import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.atc import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class ATCs:
    __dir_path: str

    atc_atis: list[ATC_ATIS]
    atc_base: list[ATC_BASE]
    atc_rmk: list[ATC_RMK]
    atc_svc: list[ATC_SVC]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.atc_atis = []
        self.atc_base = []
        self.atc_rmk = []
        self.atc_svc = []

    def parse(self) -> None:
        self.parse_atc_atis()
        self.parse_atc_base()
        self.parse_atc_rmk()
        self.parse_atc_svc()

    def parse_atc_atis(self) -> None:
        file_path = path.join(self.__dir_path, ATC_ATIS_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {ATC_ATIS_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = ATC_ATIS(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    facility_type=row["FACILITY_TYPE"],
                    state_code=row["STATE_CODE"],
                    facility_id=row["FACILITY_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    atis_no=row["ATIS_NO"],
                    description=row["DESCRIPTION"],
                    atis_hrs=row["ATIS_HRS"],
                    atis_phone_no=row["ATIS_PHONE_NO"],
                )
                self.atc_atis.append(record)

    def parse_atc_base(self) -> None:
        file_path = path.join(self.__dir_path, ATC_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {ATC_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = ATC_BASE(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    facility_type=row["FACILITY_TYPE"],
                    state_code=row["STATE_CODE"],
                    facility_id=row["FACILITY_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    icao_id=row["ICAO_ID"],
                    facility_name=row["FACILITY_NAME"],
                    region_code=row["REGION_CODE"],
                    twr_operator_code=row["TWR_OPERATOR_CODE"],
                    twr_call=row["TWR_CALL"],
                    twr_hrs=row["TWR_HRS"],
                    primary_apch_radio_call=row["PRIMARY_APCH_RADIO_CALL"],
                    apch_p_provider=row["APCH_P_PROVIDER"],
                    apch_p_prov_type_cd=row["APCH_P_PROV_TYPE_CD"],
                    secondary_apch_radio_call=row["SECONDARY_APCH_RADIO_CALL"],
                    apch_s_provider=row["APCH_S_PROVIDER"],
                    apch_s_prov_type_cd=row["APCH_S_PROV_TYPE_CD"],
                    primary_dep_radio_call=row["PRIMARY_DEP_RADIO_CALL"],
                    dep_p_provider=row["DEP_P_PROVIDER"],
                    dep_p_prov_type_cd=row["DEP_P_PROV_TYPE_CD"],
                    secondary_dep_radio_call=row["SECONDARY_DEP_RADIO_CALL"],
                    dep_s_provider=row["DEP_S_PROVIDER"],
                    dep_s_prov_type_cd=row["DEP_S_PROV_TYPE_CD"],
                    ctl_fac_apch_dep_calls=row["CTL_FAC_APCH_DEP_CALLS"],
                    apch_dep_oper_code=row["APCH_DEP_OPER_CODE"],
                    ctl_prvding_hrs=row["CTL_PRVDING_HRS"],
                    secondary_ctl_prvding_hrs=row["SECONDARY_CTL_PRVDING_HRS"],
                )
                self.atc_base.append(record)

    def parse_atc_rmk(self) -> None:
        file_path = path.join(self.__dir_path, ATC_RMK_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {ATC_RMK_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = ATC_RMK(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    facility_type=row["FACILITY_TYPE"],
                    state_code=row["STATE_CODE"],
                    facility_id=row["FACILITY_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    legacy_element_number=row["LEGACY_ELEMENT_NUMBER"],
                    tab_name=row["TAB_NAME"],
                    ref_col_name=row["REF_COL_NAME"],
                    remark_no=row["REMARK_NO"],
                    remark=row["REMARK"],
                )
                self.atc_rmk.append(record)

    def parse_atc_svc(self) -> None:
        file_path = path.join(self.__dir_path, ATC_SVC_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {ATC_SVC_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = ATC_SVC(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    facility_type=row["FACILITY_TYPE"],
                    state_code=row["STATE_CODE"],
                    facility_id=row["FACILITY_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    ctl_svc=row["CTL_SVC"],
                )
                self.atc_svc.append(record)

    def to_dict(self) -> dict:
        return {
            **self.atc_atis_to_dict(),
            **self.atc_base_to_dict(),
            **self.atc_rmk_to_dict(),
            **self.atc_svc_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.atc_atis_to_db(db_cursor)
        self.atc_base_to_db(db_cursor)
        self.atc_rmk_to_db(db_cursor)
        self.atc_svc_to_db(db_cursor)

    def atc_atis_to_dict(self) -> dict:
        return {"atc_atis": [item.to_dict() for item in self.atc_atis]}

    def atc_base_to_dict(self) -> dict:
        return {"atc_base": [item.to_dict() for item in self.atc_base]}

    def atc_rmk_to_dict(self) -> dict:
        return {"atc_rmk": [item.to_dict() for item in self.atc_rmk]}

    def atc_svc_to_dict(self) -> dict:
        return {"atc_svc": [item.to_dict() for item in self.atc_svc]}

    def atc_atis_to_db(self, db_cursor: Cursor) -> None:
        if len(self.atc_atis) > 0:
            print(f"               Processing {ATC_ATIS_FILE_NAME}")
            process_table(db_cursor, self.atc_atis)

    def atc_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.atc_base) > 0:
            print(f"               Processing {ATC_BASE_FILE_NAME}")
            process_table(db_cursor, self.atc_base)

    def atc_rmk_to_db(self, db_cursor: Cursor) -> None:
        if len(self.atc_rmk) > 0:
            print(f"               Processing {ATC_RMK_FILE_NAME}")
            process_table(db_cursor, self.atc_rmk)

    def atc_svc_to_db(self, db_cursor: Cursor) -> None:
        if len(self.atc_svc) > 0:
            print(f"               Processing {ATC_SVC_FILE_NAME}")
            process_table(db_cursor, self.atc_svc)
