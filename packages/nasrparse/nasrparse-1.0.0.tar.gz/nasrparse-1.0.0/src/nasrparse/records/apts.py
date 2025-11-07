from nasrparse.records.apt import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.apt import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class APTs:
    __dir_path: str

    apt_ars: list[APT_ARS]
    apt_att: list[APT_ATT]
    apt_base: list[APT_BASE]
    apt_con: list[APT_CON]
    apt_rmk: list[APT_RMK]
    apt_rwy: list[APT_RWY]
    apt_rwy_end: list[APT_RWY_END]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.apt_ars = []
        self.apt_att = []
        self.apt_base = []
        self.apt_con = []
        self.apt_rmk = []
        self.apt_rwy = []
        self.apt_rwy_end = []

    def parse(self) -> None:
        self.parse_apt_ars()
        self.parse_apt_att()
        self.parse_apt_base()
        self.parse_apt_con()
        self.parse_apt_rmk()
        self.parse_apt_rwy()
        self.parse_apt_rwy_end()

    def parse_apt_ars(self) -> None:
        file_path = path.join(self.__dir_path, APT_ARS_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {APT_ARS_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = APT_ARS(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    state_code=row["STATE_CODE"],
                    arpt_id=row["ARPT_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    rwy_id=row["RWY_ID"],
                    rwy_end_id=row["RWY_END_ID"],
                    arrest_device_code=row["ARREST_DEVICE_CODE"],
                )
                self.apt_ars.append(record)

    def parse_apt_att(self) -> None:
        file_path = path.join(self.__dir_path, APT_ATT_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {APT_ATT_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = APT_ATT(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    state_code=row["STATE_CODE"],
                    arpt_id=row["ARPT_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    sked_seq_no=row["SKED_SEQ_NO"],
                    month=row["MONTH"],
                    day=row["DAY"],
                    hour=row["HOUR"],
                )
                self.apt_att.append(record)

    def parse_apt_base(self) -> None:
        file_path = path.join(self.__dir_path, APT_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {APT_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = APT_BASE(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    state_code=row["STATE_CODE"],
                    arpt_id=row["ARPT_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    region_code=row["REGION_CODE"],
                    ado_code=row["ADO_CODE"],
                    state_name=row["STATE_NAME"],
                    county_name=row["COUNTY_NAME"],
                    county_assoc_state=row["COUNTY_ASSOC_STATE"],
                    arpt_name=row["ARPT_NAME"],
                    ownership_type_code=row["OWNERSHIP_TYPE_CODE"],
                    facility_use_code=row["FACILITY_USE_CODE"],
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
                    survey_method_code=row["SURVEY_METHOD_CODE"],
                    elev=row["ELEV"],
                    elev_method_code=row["ELEV_METHOD_CODE"],
                    mag_varn=row["MAG_VARN"],
                    mag_hemis=row["MAG_HEMIS"],
                    mag_varn_year=row["MAG_VARN_YEAR"],
                    tpa=row["TPA"],
                    chart_name=row["CHART_NAME"],
                    dist_city_to_airport=row["DIST_CITY_TO_AIRPORT"],
                    direction_code=row["DIRECTION_CODE"],
                    acreage=row["ACREAGE"],
                    resp_artcc_id=row["RESP_ARTCC_ID"],
                    computer_id=row["COMPUTER_ID"],
                    artcc_name=row["ARTCC_NAME"],
                    fss_on_arpt_flag=row["FSS_ON_ARPT_FLAG"],
                    fss_id=row["FSS_ID"],
                    fss_name=row["FSS_NAME"],
                    phone_no=row["PHONE_NO"],
                    toll_free_no=row["TOLL_FREE_NO"],
                    alt_fss_id=row["ALT_FSS_ID"],
                    alt_fss_name=row["ALT_FSS_NAME"],
                    alt_toll_free_no=row["ALT_TOLL_FREE_NO"],
                    notam_id=row["NOTAM_ID"],
                    notam_flag=row["NOTAM_FLAG"],
                    activation_date=row["ACTIVATION_DATE"],
                    arpt_status=row["ARPT_STATUS"],
                    far_139_type_code=row["FAR_139_TYPE_CODE"],
                    far_139_carrier_ser_code=row["FAR_139_CARRIER_SER_CODE"],
                    arff_cert_type_date=row["ARFF_CERT_TYPE_DATE"],
                    nasp_code=row["NASP_CODE"],
                    asp_anlys_dtrm_code=row["ASP_ANLYS_DTRM_CODE"],
                    cust_flag=row["CUST_FLAG"],
                    lndg_rights_flag=row["LNDG_RIGHTS_FLAG"],
                    joint_use_flag=row["JOINT_USE_FLAG"],
                    mil_lndg_flag=row["MIL_LNDG_FLAG"],
                    inspect_method_code=row["INSPECT_METHOD_CODE"],
                    inspector_code=row["INSPECTOR_CODE"],
                    last_inspection=row["LAST_INSPECTION"],
                    last_info_response=row["LAST_INFO_RESPONSE"],
                    fuel_types=row["FUEL_TYPES"],
                    airframe_repair_ser_code=row["AIRFRAME_REPAIR_SER_CODE"],
                    pwr_plant_repair_ser=row["PWR_PLANT_REPAIR_SER"],
                    bottled_oxy_type=row["BOTTLED_OXY_TYPE"],
                    bulk_oxy_type=row["BULK_OXY_TYPE"],
                    lgt_sked=row["LGT_SKED"],
                    bcn_lgt_sked=row["BCN_LGT_SKED"],
                    twr_type_code=row["TWR_TYPE_CODE"],
                    seg_circle_mkr_flag=row["SEG_CIRCLE_MKR_FLAG"],
                    bcn_lens_color=row["BCN_LENS_COLOR"],
                    lndg_fee_flag=row["LNDG_FEE_FLAG"],
                    medical_use_flag=row["MEDICAL_USE_FLAG"],
                    arpt_psn_source=row["ARPT_PSN_SOURCE"],
                    position_src_date=row["POSITION_SRC_DATE"],
                    arpt_elev_source=row["ARPT_ELEV_SOURCE"],
                    elevation_src_date=row["ELEVATION_SRC_DATE"],
                    contr_fuel_avbl=row["CONTR_FUEL_AVBL"],
                    trns_strg_buoy_flag=row["TRNS_STRG_BUOY_FLAG"],
                    trns_strg_hgr_flag=row["TRNS_STRG_HGR_FLAG"],
                    trns_strg_tie_flag=row["TRNS_STRG_TIE_FLAG"],
                    other_services=row["OTHER_SERVICES"],
                    wind_indcr_flag=row["WIND_INDCR_FLAG"],
                    icao_id=row["ICAO_ID"],
                    min_op_network=row["MIN_OP_NETWORK"],
                    user_fee_flag=row["USER_FEE_FLAG"],
                    cta=row["CTA"],
                )
                self.apt_base.append(record)

    def parse_apt_con(self) -> None:
        file_path = path.join(self.__dir_path, APT_CON_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {APT_CON_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = APT_CON(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    state_code=row["STATE_CODE"],
                    arpt_id=row["ARPT_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    title=row["TITLE"],
                    name=row["NAME"],
                    address1=row["ADDRESS1"],
                    address2=row["ADDRESS2"],
                    title_city=row["TITLE_CITY"],
                    state=row["STATE"],
                    zip_code=row["ZIP_CODE"],
                    zip_plus_four=row["ZIP_PLUS_FOUR"],
                    phone_no=row["PHONE_NO"],
                )
                self.apt_con.append(record)

    def parse_apt_rmk(self) -> None:
        file_path = path.join(self.__dir_path, APT_RMK_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {APT_RMK_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = APT_RMK(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    state_code=row["STATE_CODE"],
                    arpt_id=row["ARPT_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    legacy_element_number=row["LEGACY_ELEMENT_NUMBER"],
                    tab_name=row["TAB_NAME"],
                    ref_col_name=row["REF_COL_NAME"],
                    element=row["ELEMENT"],
                    ref_col_seq_no=row["REF_COL_SEQ_NO"],
                    remark=row["REMARK"],
                )
                self.apt_rmk.append(record)

    def parse_apt_rwy(self) -> None:
        file_path = path.join(self.__dir_path, APT_RWY_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {APT_RWY_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = APT_RWY(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    state_code=row["STATE_CODE"],
                    arpt_id=row["ARPT_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    rwy_id=row["RWY_ID"],
                    rwy_len=row["RWY_LEN"],
                    rwy_width=row["RWY_WIDTH"],
                    surface_type_code=row["SURFACE_TYPE_CODE"],
                    cond=row["COND"],
                    treatment_code=row["TREATMENT_CODE"],
                    pcn=row["PCN"],
                    pavement_type_code=row["PAVEMENT_TYPE_CODE"],
                    subgrade_strength_code=row["SUBGRADE_STRENGTH_CODE"],
                    tire_pres_code=row["TIRE_PRES_CODE"],
                    dtrm_method_code=row["DTRM_METHOD_CODE"],
                    rwy_lgt_code=row["RWY_LGT_CODE"],
                    rwy_len_source=row["RWY_LEN_SOURCE"],
                    length_source_date=row["LENGTH_SOURCE_DATE"],
                    gross_wt_sw=row["GROSS_WT_SW"],
                    gross_wt_dw=row["GROSS_WT_DW"],
                    gross_wt_dtw=row["GROSS_WT_DTW"],
                    gross_wt_ddtw=row["GROSS_WT_DDTW"],
                )
                self.apt_rwy.append(record)

    def parse_apt_rwy_end(self) -> None:
        file_path = path.join(self.__dir_path, APT_RWY_END_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {APT_RWY_END_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = APT_RWY_END(
                    eff_date=row["EFF_DATE"],
                    site_no=row["SITE_NO"],
                    site_type_code=row["SITE_TYPE_CODE"],
                    state_code=row["STATE_CODE"],
                    arpt_id=row["ARPT_ID"],
                    city=row["CITY"],
                    country_code=row["COUNTRY_CODE"],
                    rwy_id=row["RWY_ID"],
                    rwy_end_id=row["RWY_END_ID"],
                    true_alignment=row["TRUE_ALIGNMENT"],
                    ils_type=row["ILS_TYPE"],
                    right_hand_traffic_pat_flag=row["RIGHT_HAND_TRAFFIC_PAT_FLAG"],
                    rwy_marking_type_code=row["RWY_MARKING_TYPE_CODE"],
                    rwy_marking_cond=row["RWY_MARKING_COND"],
                    rwy_end_lat_deg=row["RWY_END_LAT_DEG"],
                    rwy_end_lat_min=row["RWY_END_LAT_MIN"],
                    rwy_end_lat_sec=row["RWY_END_LAT_SEC"],
                    rwy_end_lat_hemis=row["RWY_END_LAT_HEMIS"],
                    lat_decimal=row["LAT_DECIMAL"],
                    rwy_end_lon_deg=row["RWY_END_LONG_DEG"],
                    rwy_end_lon_min=row["RWY_END_LONG_MIN"],
                    rwy_end_lon_sec=row["RWY_END_LONG_SEC"],
                    rwy_end_lon_hemis=row["RWY_END_LONG_HEMIS"],
                    lon_decimal=row["LONG_DECIMAL"],
                    rwy_end_elev=row["RWY_END_ELEV"],
                    thr_crossing_hgt=row["THR_CROSSING_HGT"],
                    visual_glide_path_angle=row["VISUAL_GLIDE_PATH_ANGLE"],
                    displaced_thr_lat_deg=row["DISPLACED_THR_LAT_DEG"],
                    displaced_thr_lat_min=row["DISPLACED_THR_LAT_MIN"],
                    displaced_thr_lat_sec=row["DISPLACED_THR_LAT_SEC"],
                    displaced_thr_lat_hemis=row["DISPLACED_THR_LAT_HEMIS"],
                    lat_displaced_thr_decimal=row["LAT_DISPLACED_THR_DECIMAL"],
                    displaced_thr_lon_deg=row["DISPLACED_THR_LONG_DEG"],
                    displaced_thr_lon_min=row["DISPLACED_THR_LONG_MIN"],
                    displaced_thr_lon_sec=row["DISPLACED_THR_LONG_SEC"],
                    displaced_thr_lon_hemis=row["DISPLACED_THR_LONG_HEMIS"],
                    lon_displaced_thr_decimal=row["LONG_DISPLACED_THR_DECIMAL"],
                    displaced_thr_elev=row["DISPLACED_THR_ELEV"],
                    displaced_thr_len=row["DISPLACED_THR_LEN"],
                    tdz_elev=row["TDZ_ELEV"],
                    vgsi_code=row["VGSI_CODE"],
                    rwy_visual_range_equip_code=row["RWY_VISUAL_RANGE_EQUIP_CODE"],
                    rwy_vsby_value_equip_flag=row["RWY_VSBY_VALUE_EQUIP_FLAG"],
                    apch_lgt_system_code=row["APCH_LGT_SYSTEM_CODE"],
                    rwy_end_lgts_flag=row["RWY_END_LGTS_FLAG"],
                    cntrln_lgts_avbl_flag=row["CNTRLN_LGTS_AVBL_FLAG"],
                    tdz_lgt_avbl_flag=row["TDZ_LGT_AVBL_FLAG"],
                    obstn_type=row["OBSTN_TYPE"],
                    obstn_mrkd_code=row["OBSTN_MRKD_CODE"],
                    far_part_77_code=row["FAR_PART_77_CODE"],
                    obstn_clnc_slope=row["OBSTN_CLNC_SLOPE"],
                    obstn_hgt=row["OBSTN_HGT"],
                    dist_from_thr=row["DIST_FROM_THR"],
                    cntrln_offset=row["CNTRLN_OFFSET"],
                    cntrln_dir_code=row["CNTRLN_DIR_CODE"],
                    rwy_grad=row["RWY_GRAD"],
                    rwy_grad_direction=row["RWY_GRAD_DIRECTION"],
                    rwy_end_psn_source=row["RWY_END_PSN_SOURCE"],
                    rwy_end_psn_date=row["RWY_END_PSN_DATE"],
                    rwy_end_elev_source=row["RWY_END_ELEV_SOURCE"],
                    rwy_end_elev_date=row["RWY_END_ELEV_DATE"],
                    dspl_thr_psn_source=row["DSPL_THR_PSN_SOURCE"],
                    rwy_end_dspl_thr_psn_date=row["RWY_END_DSPL_THR_PSN_DATE"],
                    dspl_thr_elev_source=row["DSPL_THR_ELEV_SOURCE"],
                    rwy_end_dspl_thr_elev_date=row["RWY_END_DSPL_THR_ELEV_DATE"],
                    tkof_run_avbl=row["TKOF_RUN_AVBL"],
                    tkof_dist_avbl=row["TKOF_DIST_AVBL"],
                    aclt_stop_dist_avbl=row["ACLT_STOP_DIST_AVBL"],
                    lndg_dist_avbl=row["LNDG_DIST_AVBL"],
                    lahso_ald=row["LAHSO_ALD"],
                    rwy_end_intersect_lahso=row["RWY_END_INTERSECT_LAHSO"],
                    lahso_desc=row["LAHSO_DESC"],
                    lahso_lat=row["LAHSO_LAT"],
                    lat_lahso_decimal=row["LAT_LAHSO_DECIMAL"],
                    lahso_lon=row["LAHSO_LONG"],
                    lon_lahso_decimal=row["LONG_LAHSO_DECIMAL"],
                    lahso_psn_source=row["LAHSO_PSN_SOURCE"],
                    rwy_end_lahso_psn_date=row["RWY_END_LAHSO_PSN_DATE"],
                )
                self.apt_rwy_end.append(record)

    def to_dict(self) -> dict:
        return {
            **self.apt_ars_to_dict(),
            **self.apt_att_to_dict(),
            **self.apt_base_to_dict(),
            **self.apt_con_to_dict(),
            **self.apt_rmk_to_dict(),
            **self.apt_rwy_to_dict(),
            **self.apt_rwy_end_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.apt_ars_to_db(db_cursor)
        self.apt_att_to_db(db_cursor)
        self.apt_base_to_db(db_cursor)
        self.apt_con_to_db(db_cursor)
        self.apt_rmk_to_db(db_cursor)
        self.apt_rwy_to_db(db_cursor)
        self.apt_rwy_end_to_db(db_cursor)

    def apt_ars_to_dict(self) -> dict:
        return {"apt_ars": [item.to_dict() for item in self.apt_ars]}

    def apt_att_to_dict(self) -> dict:
        return {"apt_att": [item.to_dict() for item in self.apt_att]}

    def apt_base_to_dict(self) -> dict:
        return {"apt_base": [item.to_dict() for item in self.apt_base]}

    def apt_con_to_dict(self) -> dict:
        return {"apt_con": [item.to_dict() for item in self.apt_con]}

    def apt_rmk_to_dict(self) -> dict:
        return {"apt_rmk": [item.to_dict() for item in self.apt_rmk]}

    def apt_rwy_to_dict(self) -> dict:
        return {"apt_rwy": [item.to_dict() for item in self.apt_rwy]}

    def apt_rwy_end_to_dict(self) -> dict:
        return {"apt_rwy_end": [item.to_dict() for item in self.apt_rwy_end]}

    def apt_ars_to_db(self, db_cursor: Cursor) -> None:
        if len(self.apt_ars) > 0:
            print(f"               Processing {APT_ARS_FILE_NAME}")
            process_table(db_cursor, self.apt_ars)

    def apt_att_to_db(self, db_cursor: Cursor) -> None:
        if len(self.apt_att) > 0:
            print(f"               Processing {APT_ATT_FILE_NAME}")
            process_table(db_cursor, self.apt_att)

    def apt_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.apt_base) > 0:
            print(f"               Processing {APT_BASE_FILE_NAME}")
            process_table(db_cursor, self.apt_base)

    def apt_con_to_db(self, db_cursor: Cursor) -> None:
        if len(self.apt_con) > 0:
            print(f"               Processing {APT_CON_FILE_NAME}")
            process_table(db_cursor, self.apt_con)

    def apt_rmk_to_db(self, db_cursor: Cursor) -> None:
        if len(self.apt_rmk) > 0:
            print(f"               Processing {APT_RMK_FILE_NAME}")
            process_table(db_cursor, self.apt_rmk)

    def apt_rwy_to_db(self, db_cursor: Cursor) -> None:
        if len(self.apt_rwy) > 0:
            print(f"               Processing {APT_RWY_FILE_NAME}")
            process_table(db_cursor, self.apt_rwy)

    def apt_rwy_end_to_db(self, db_cursor: Cursor) -> None:
        if len(self.apt_rwy_end) > 0:
            print(f"               Processing {APT_RWY_END_FILE_NAME}")
            process_table(db_cursor, self.apt_rwy_end)
