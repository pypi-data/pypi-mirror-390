from nasrparse.records.nav import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.nav import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class NAVs:
    __dir_path: str

    nav_base: list[NAV_BASE]
    nav_rmk: list[NAV_RMK]
    nav_ckpt: list[NAV_CKPT]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.nav_base = []
        self.nav_rmk = []
        self.nav_ckpt = []

    def parse(self) -> None:
        self.parse_nav_base()
        self.parse_nav_rmk()
        self.parse_nav_ckpt()

    def parse_nav_base(self) -> None:
        file_path = path.join(self.__dir_path, NAV_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {NAV_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = NAV_BASE(
                    eff_date=row["EFF_DATE"],
                    nav_id=row["NAV_ID"],
                    nav_type=row["NAV_TYPE"],
                    state_code=row["STATE_CODE"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    nav_status=row["NAV_STATUS"],
                    name=row["NAME"],
                    state_name=row["STATE_NAME"],
                    region_code=row["REGION_CODE"],
                    country_name=row["COUNTRY_NAME"],
                    fan_marker=row["FAN_MARKER"],
                    owner=row["OWNER"],
                    operator=row["OPERATOR"],
                    nas_use_flag=row["NAS_USE_FLAG"],
                    public_use_flag=row["PUBLIC_USE_FLAG"],
                    ndb_class_code=row["NDB_CLASS_CODE"],
                    oper_hours=row["OPER_HOURS"],
                    high_alt_artcc_id=row["HIGH_ALT_ARTCC_ID"],
                    high_artcc_name=row["HIGH_ARTCC_NAME"],
                    low_alt_artcc_id=row["LOW_ALT_ARTCC_ID"],
                    low_artcc_name=row["LOW_ARTCC_NAME"],
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
                    survey_accuracy_code=row["SURVEY_ACCURACY_CODE"],
                    tacan_dme_status=row["TACAN_DME_STATUS"],
                    tacan_dme_lat_deg=row["TACAN_DME_LAT_DEG"],
                    tacan_dme_lat_min=row["TACAN_DME_LAT_MIN"],
                    tacan_dme_lat_sec=row["TACAN_DME_LAT_SEC"],
                    tacan_dme_lat_hemis=row["TACAN_DME_LAT_HEMIS"],
                    tacan_dme_lat_decimal=row["TACAN_DME_LAT_DECIMAL"],
                    tacan_dme_lon_deg=row["TACAN_DME_LONG_DEG"],
                    tacan_dme_lon_min=row["TACAN_DME_LONG_MIN"],
                    tacan_dme_lon_sec=row["TACAN_DME_LONG_SEC"],
                    tacan_dme_lon_hemis=row["TACAN_DME_LONG_HEMIS"],
                    tacan_dme_lon_decimal=row["TACAN_DME_LONG_DECIMAL"],
                    elev=row["ELEV"],
                    mag_varn=row["MAG_VARN"],
                    mag_varn_hemis=row["MAG_VARN_HEMIS"],
                    mag_varn_year=row["MAG_VARN_YEAR"],
                    simul_voice_flag=row["SIMUL_VOICE_FLAG"],
                    pwr_output=row["PWR_OUTPUT"],
                    auto_voice_id_flag=row["AUTO_VOICE_ID_FLAG"],
                    mnt_cat_code=row["MNT_CAT_CODE"],
                    voice_call=row["VOICE_CALL"],
                    chan=row["CHAN"],
                    freq=row["FREQ"],
                    mkr_ident=row["MKR_IDENT"],
                    mkr_shape=row["MKR_SHAPE"],
                    mkr_brg=row["MKR_BRG"],
                    alt_code=row["ALT_CODE"],
                    dme_ssv=row["DME_SSV"],
                    low_nav_on_high_chart_flag=row["LOW_NAV_ON_HIGH_CHART_FLAG"],
                    z_mkr_flag=row["Z_MKR_FLAG"],
                    fss_id=row["FSS_ID"],
                    fss_name=row["FSS_NAME"],
                    fss_hours=row["FSS_HOURS"],
                    notam_id=row["NOTAM_ID"],
                    quad_ident=row["QUAD_IDENT"],
                    pitch_flag=row["PITCH_FLAG"],
                    catch_flag=row["CATCH_FLAG"],
                    sua_atcaa_flag=row["SUA_ATCAA_FLAG"],
                    restriction_flag=row["RESTRICTION_FLAG"],
                    hiwas_flag=row["HIWAS_FLAG"],
                )
                self.nav_base.append(record)

    def parse_nav_rmk(self) -> None:
        file_path = path.join(self.__dir_path, NAV_RMK_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {NAV_RMK_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = NAV_RMK(
                    eff_date=row["EFF_DATE"],
                    nav_id=row["NAV_ID"],
                    nav_type=row["NAV_TYPE"],
                    state_code=row["STATE_CODE"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    tab_name=row["TAB_NAME"],
                    ref_col_name=row["REF_COL_NAME"],
                    ref_col_seq_no=row["REF_COL_SEQ_NO"],
                    remark=row["REMARK"],
                )
                self.nav_rmk.append(record)

    def parse_nav_ckpt(self) -> None:
        file_path = path.join(self.__dir_path, NAV_CKPT_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {NAV_CKPT_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = NAV_CKPT(
                    eff_date=row["EFF_DATE"],
                    nav_id=row["NAV_ID"],
                    nav_type=row["NAV_TYPE"],
                    state_code=row["STATE_CODE"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    altitude=row["ALTITUDE"],
                    brg=row["BRG"],
                    air_gnd_code=row["AIR_GND_CODE"],
                    chk_desc=row["CHK_DESC"],
                    arpt_id=row["ARPT_ID"],
                    state_chk_code=row["STATE_CHK_CODE"],
                )
                self.nav_ckpt.append(record)

    def to_dict(self) -> dict:
        return {
            **self.nav_base_to_dict(),
            **self.nav_rmk_to_dict(),
            **self.nav_ckpt_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.nav_base_to_db(db_cursor)
        self.nav_rmk_to_db(db_cursor)
        self.nav_ckpt_to_db(db_cursor)

    def nav_base_to_dict(self) -> dict:
        return {"nav_base": [item.to_dict() for item in self.nav_base]}

    def nav_rmk_to_dict(self) -> dict:
        return {"nav_rmk": [item.to_dict() for item in self.nav_rmk]}

    def nav_ckpt_to_dict(self) -> dict:
        return {"nav_ckpt": [item.to_dict() for item in self.nav_ckpt]}

    def nav_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.nav_base) > 0:
            print(f"               Processing {NAV_BASE_FILE_NAME}")
            process_table(db_cursor, self.nav_base)

    def nav_rmk_to_db(self, db_cursor: Cursor) -> None:
        if len(self.nav_rmk) > 0:
            print(f"               Processing {NAV_RMK_FILE_NAME}")
            process_table(db_cursor, self.nav_rmk)

    def nav_ckpt_to_db(self, db_cursor: Cursor) -> None:
        if len(self.nav_ckpt) > 0:
            print(f"               Processing {NAV_CKPT_FILE_NAME}")
            process_table(db_cursor, self.nav_ckpt)
