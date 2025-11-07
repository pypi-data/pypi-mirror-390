from nasrparse.functions.record import (
    to_nullable_bool,
    to_nullable_date,
    to_nullable_float,
    to_nullable_int,
    to_nullable_string,
)
from nasrparse.records.types import (
    ApproachLightCode,
    HemisCode,
    ILSCode,
    ObstructionMarkingCode,
    Part77Code,
    RunwayMarkCode,
    RunwayMarkCondCode,
    RVRCode,
    VGSICode,
)

from ._base import Base

from datetime import date


class APT_RWY_END(Base):
    rwy_id: str | None
    """Runway Identification"""
    rwy_end_id: str | None
    """Runway End Identifier"""
    true_alignment: int | None
    """Runway End True Alignment (True Heading of the Runway - to the nearest Degree.)"""
    ils_type: ILSCode
    """Instrument Landing System (ILS) Type"""
    right_hand_traffic_pat_flag: bool | None
    """Right Hand Traffic Pattern for Landing Aircraft"""
    rwy_marking_type_code: RunwayMarkCode
    """Runway Markings (Type)"""
    rwy_marking_cond: RunwayMarkCondCode
    """Runway Markings (Condition)"""
    rwy_end_lat_deg: int | None
    """Latitude Degrees of Physical Runway End"""
    rwy_end_lat_min: int | None
    """Latitude Minutes of Physical Runway End"""
    rwy_end_lat_sec: float | None
    """Latitude Seconds of Physical Runway End"""
    rwy_end_lat_hemis: HemisCode
    """Latitude Hemisphere of Physical Runway End"""
    lat_decimal: float | None
    """Latitude of Physical Runway End in Decimal Format"""
    rwy_end_lon_deg: int | None
    """Longitude Degrees of Physical Runway End"""
    rwy_end_lon_min: int | None
    """Longitude Minutes of Physical Runway End"""
    rwy_end_lon_sec: float | None
    """Longitude Seconds of Physical Runway End"""
    rwy_end_lon_hemis: HemisCode
    """Longitude Hemisphere of Physical Runway End"""
    lon_decimal: float | None
    """Longitude of Physical Runway End in Decimal Format"""
    rwy_end_elev: float | None
    """Elevation (Feet MSL) at Physical Runway End"""
    thr_crossing_hgt: int | None
    """Threshold Crossing Height (Feet AGL) Height that the Effective Visual Glide Path Crosses Above the Runway Threshold."""
    visual_glide_path_angle: float | None
    """Visual Glide Path Angle (Hundredths of Degrees)"""
    displaced_thr_lat_deg: int | None
    """Latitude Degrees at Displace Threshold"""
    displaced_thr_lat_min: int | None
    """Latitude Minutes at Displace Threshold"""
    displaced_thr_lat_sec: float | None
    """Latitude Seconds at Displace Threshold"""
    displaced_thr_lat_hemis: HemisCode
    """Latitude Hemisphere at Displace Threshold"""
    lat_displaced_thr_decimal: float | None
    """Latitude at Displace Threshold in Decimal Format"""
    displaced_thr_lon_deg: int | None
    """Longitude Degrees at Displace Threshold"""
    displaced_thr_lon_min: int | None
    """Longitude Minutes at Displace Threshold"""
    displaced_thr_lon_sec: float | None
    """Longitude Seconds at Displace Threshold"""
    displaced_thr_lon_hemis: HemisCode
    """Longitude Hemisphere at Displace Threshold"""
    lon_displaced_thr_decimal: float | None
    """Longitude at Displace Threshold in Decimal Format"""
    displaced_thr_elev: float | None
    """Elevation at Displaced Threshold (Feet MSL)"""
    displaced_thr_len: int | None
    """Displaced Threshold - Length in Feet from Runway End"""
    tdz_elev: float | None
    """Elevation at Touchdown Zone (Feet MSL)"""
    vgsi_code: VGSICode
    """Visual Glide Slope Indicators"""
    rwy_visual_range_equip_code: RVRCode
    """Runway Visual Range Equipment (RVR) indicates location(s) at which RVR equipment is installed."""
    rwy_vsby_value_equip_flag: bool | None
    """Runway Visibility Value Equipment (RVV) indicates presence of RVV equipment"""
    apch_lgt_system_code: ApproachLightCode
    """Approach Light System"""
    rwy_end_lgts_flag: bool | None
    """Runway End Identifier Lights (REIL) Availability"""
    cntrln_lgts_avbl_flag: bool | None
    """Runway Centerline Lights Availability"""
    tdz_lgt_avbl_flag: bool | None
    """Runway End Touchdown Lights Availability"""
    obstn_type: str | None
    """Controlling Object Description"""
    obstn_mrkd_code: ObstructionMarkingCode
    """Controlling Object Marked/Lighted"""
    far_part_77_code: Part77Code
    """FAA CFR Part 77 (Objects Affecting Navigable Airspace) Runway Category"""
    obstn_clnc_slope: str | None
    """Controlling Object Clearance Slope value, expressed as a ratio of N:1, of the Clearance that is available to approaching aircraft."""
    obstn_hgt: int | None
    """Controlling Object Height Above Runway (In Feet AGL) The Object Is Above The Physical Runway End."""
    dist_from_thr: int | None
    """Controlling Object Distance from Runway End Distance, in feet, from the Physical Runway End to the Controlling Object. This is measured using the extended runway centerline to a point abeam the object."""
    cntrln_offset: int | None
    """Controlling Object Centerline Offset Distance, in feet, that the Controlling Object is located away from the extended Runway Centerline as measured horizontally on a line perpendicular to the extended Runway Centerline."""
    cntrln_dir_code: str | None
    """Controlling Object Centerline Offset Direction indicates the direction (left or right) to the object from the centerline as seen by an approaching pilot."""
    rwy_grad: float | None
    """Runway End Gradient"""
    rwy_grad_direction: str | None
    """Runway End Gradient Direction (Up Or Down)"""
    rwy_end_psn_source: str | None
    """Runway End Position Source"""
    rwy_end_psn_date: date | None
    """Runway End Position Source Date (YYYY/MM/DD)"""
    rwy_end_elev_source: str | None
    """Runway End Elevation Source"""
    rwy_end_elev_date: date | None
    """Runway End Elevation Source Date (YYYY/MM/DD)"""
    dspl_thr_psn_source: str | None
    """Displaced Threshold Position Source"""
    rwy_end_dspl_thr_psn_date: date | None
    """Displaced Threshold Position Source Date (YYYY/MM/DD)"""
    dspl_thr_elev_source: str | None
    """Displaced Threshold Elevation Source"""
    rwy_end_dspl_thr_elev_date: date | None
    """Displaced Threshold Elevation Source Date (YYYY/MM/DD)"""
    tkof_run_avbl: int | None
    """Takeoff Run Available (TORA), In Feet"""
    tkof_dist_avbl: int | None
    """Takeoff Distance Available (TODA), In Feet"""
    aclt_stop_dist_avbl: int | None
    """Accelerate Stop Distance Available (ASDA), In Feet"""
    lndg_dist_avbl: int | None
    """Landing Distance Available (LDA), In Feet"""
    lahso_ald: int | None
    """Available Landing Distance for Land and Hold Short Operations (LAHSO)"""
    rwy_end_intersect_lahso: str | None
    """ID of Intersecting Runway Defining Hold Short Point"""
    lahso_desc: str | None
    """Description of Entity Defining Hold Short Point If Not an Intersecting Runway"""
    lahso_lat: str | None
    """Latitude of LAHSO Hold Short Point (Formatted)"""
    lat_lahso_decimal: float | None
    """Latitude of LAHSO Hold Short Point in Decimal Format"""
    lahso_lon: str | None
    """Longitude of LAHSO Hold Short Point (Formatted)"""
    lon_lahso_decimal: float | None
    """Longitude of LAHSO Hold Short Point in Decimal Format"""
    lahso_psn_source: str | None
    """LAHSO Hold Short Point Lat/Long Source"""
    rwy_end_lahso_psn_date: date | None
    """Hold Short Point Lat/Long Source Date (YYYY/MM/DD)"""

    def __init__(
        self,
        eff_date: str,
        site_no: str,
        site_type_code: str,
        state_code: str,
        arpt_id: str,
        city: str,
        country_code: str,
        rwy_id: str,
        rwy_end_id: str,
        true_alignment: str,
        ils_type: str,
        right_hand_traffic_pat_flag: str,
        rwy_marking_type_code: str,
        rwy_marking_cond: str,
        rwy_end_lat_deg: str,
        rwy_end_lat_min: str,
        rwy_end_lat_sec: str,
        rwy_end_lat_hemis: str,
        lat_decimal: str,
        rwy_end_lon_deg: str,
        rwy_end_lon_min: str,
        rwy_end_lon_sec: str,
        rwy_end_lon_hemis: str,
        lon_decimal: str,
        rwy_end_elev: str,
        thr_crossing_hgt: str,
        visual_glide_path_angle: str,
        displaced_thr_lat_deg: str,
        displaced_thr_lat_min: str,
        displaced_thr_lat_sec: str,
        displaced_thr_lat_hemis: str,
        lat_displaced_thr_decimal: str,
        displaced_thr_lon_deg: str,
        displaced_thr_lon_min: str,
        displaced_thr_lon_sec: str,
        displaced_thr_lon_hemis: str,
        lon_displaced_thr_decimal: str,
        displaced_thr_elev: str,
        displaced_thr_len: str,
        tdz_elev: str,
        vgsi_code: str,
        rwy_visual_range_equip_code: str,
        rwy_vsby_value_equip_flag: str,
        apch_lgt_system_code: str,
        rwy_end_lgts_flag: str,
        cntrln_lgts_avbl_flag: str,
        tdz_lgt_avbl_flag: str,
        obstn_type: str,
        obstn_mrkd_code: str,
        far_part_77_code: str,
        obstn_clnc_slope: str,
        obstn_hgt: str,
        dist_from_thr: str,
        cntrln_offset: str,
        cntrln_dir_code: str,
        rwy_grad: str,
        rwy_grad_direction: str,
        rwy_end_psn_source: str,
        rwy_end_psn_date: str,
        rwy_end_elev_source: str,
        rwy_end_elev_date: str,
        dspl_thr_psn_source: str,
        rwy_end_dspl_thr_psn_date: str,
        dspl_thr_elev_source: str,
        rwy_end_dspl_thr_elev_date: str,
        tkof_run_avbl: str,
        tkof_dist_avbl: str,
        aclt_stop_dist_avbl: str,
        lndg_dist_avbl: str,
        lahso_ald: str,
        rwy_end_intersect_lahso: str,
        lahso_desc: str,
        lahso_lat: str,
        lat_lahso_decimal: str,
        lahso_lon: str,
        lon_lahso_decimal: str,
        lahso_psn_source: str,
        rwy_end_lahso_psn_date: str,
    ) -> None:
        super().__init__(
            "airport_runway_end",
            eff_date,
            site_no,
            site_type_code,
            state_code,
            arpt_id,
            city,
            country_code,
        )
        self.rwy_id = to_nullable_string(rwy_id)
        self.rwy_end_id = to_nullable_string(rwy_end_id)
        self.true_alignment = to_nullable_int(true_alignment)
        self.ils_type = ILSCode.from_value(to_nullable_string(ils_type))
        self.right_hand_traffic_pat_flag = to_nullable_bool(right_hand_traffic_pat_flag)
        self.rwy_marking_type_code = RunwayMarkCode.from_value(
            to_nullable_string(rwy_marking_type_code)
        )
        self.rwy_marking_cond = RunwayMarkCondCode.from_value(
            to_nullable_string(rwy_marking_cond)
        )
        self.rwy_end_lat_deg = to_nullable_int(rwy_end_lat_deg)
        self.rwy_end_lat_min = to_nullable_int(rwy_end_lat_min)
        self.rwy_end_lat_sec = to_nullable_float(rwy_end_lat_sec)
        self.rwy_end_lat_hemis = HemisCode.from_value(
            to_nullable_string(rwy_end_lat_hemis)
        )
        self.lat_decimal = to_nullable_float(lat_decimal)
        self.rwy_end_lon_deg = to_nullable_int(rwy_end_lon_deg)
        self.rwy_end_lon_min = to_nullable_int(rwy_end_lon_min)
        self.rwy_end_lon_sec = to_nullable_float(rwy_end_lon_sec)
        self.rwy_end_lon_hemis = HemisCode.from_value(
            to_nullable_string(rwy_end_lon_hemis)
        )
        self.lon_decimal = to_nullable_float(lon_decimal)
        self.rwy_end_elev = to_nullable_float(rwy_end_elev)
        self.thr_crossing_hgt = to_nullable_int(thr_crossing_hgt)
        self.visual_glide_path_angle = to_nullable_float(visual_glide_path_angle)
        self.displaced_thr_lat_deg = to_nullable_int(displaced_thr_lat_deg)
        self.displaced_thr_lat_min = to_nullable_int(displaced_thr_lat_min)
        self.displaced_thr_lat_sec = to_nullable_float(displaced_thr_lat_sec)
        self.displaced_thr_lat_hemis = HemisCode.from_value(
            to_nullable_string(displaced_thr_lat_hemis)
        )
        self.lat_displaced_thr_decimal = to_nullable_float(lat_displaced_thr_decimal)
        self.displaced_thr_lon_deg = to_nullable_int(displaced_thr_lon_deg)
        self.displaced_thr_lon_min = to_nullable_int(displaced_thr_lon_min)
        self.displaced_thr_lon_sec = to_nullable_float(displaced_thr_lon_sec)
        self.displaced_thr_lon_hemis = HemisCode.from_value(
            to_nullable_string(displaced_thr_lon_hemis)
        )
        self.lon_displaced_thr_decimal = to_nullable_float(lon_displaced_thr_decimal)
        self.displaced_thr_elev = to_nullable_float(displaced_thr_elev)
        self.displaced_thr_len = to_nullable_int(displaced_thr_len)
        self.tdz_elev = to_nullable_float(tdz_elev)
        self.vgsi_code = VGSICode.from_value(to_nullable_string(vgsi_code))
        self.rwy_visual_range_equip_code = RVRCode.from_value(
            to_nullable_string(rwy_visual_range_equip_code)
        )
        self.rwy_vsby_value_equip_flag = to_nullable_bool(rwy_vsby_value_equip_flag)
        self.apch_lgt_system_code = ApproachLightCode.from_value(
            to_nullable_string(apch_lgt_system_code)
        )
        self.rwy_end_lgts_flag = to_nullable_bool(rwy_end_lgts_flag)
        self.cntrln_lgts_avbl_flag = to_nullable_bool(cntrln_lgts_avbl_flag)
        self.tdz_lgt_avbl_flag = to_nullable_bool(tdz_lgt_avbl_flag)
        self.obstn_type = to_nullable_string(obstn_type)
        self.obstn_mrkd_code = ObstructionMarkingCode.from_value(
            to_nullable_string(obstn_mrkd_code)
        )
        self.far_part_77_code = Part77Code.from_value(
            to_nullable_string(far_part_77_code)
        )
        self.obstn_clnc_slope = to_nullable_string(obstn_clnc_slope)
        self.obstn_hgt = to_nullable_int(obstn_hgt)
        self.dist_from_thr = to_nullable_int(dist_from_thr)
        self.cntrln_offset = to_nullable_int(cntrln_offset)
        self.cntrln_dir_code = to_nullable_string(cntrln_dir_code)
        self.rwy_grad = to_nullable_float(rwy_grad)
        self.rwy_grad_direction = to_nullable_string(rwy_grad_direction)
        self.rwy_end_psn_source = to_nullable_string(rwy_end_psn_source)
        self.rwy_end_psn_date = to_nullable_date(rwy_end_psn_date, "YYYY/MM/DD")
        self.rwy_end_elev_source = to_nullable_string(rwy_end_elev_source)
        self.rwy_end_elev_date = to_nullable_date(rwy_end_elev_date, "YYYY/MM/DD")
        self.dspl_thr_psn_source = to_nullable_string(dspl_thr_psn_source)
        self.rwy_end_dspl_thr_psn_date = to_nullable_date(
            rwy_end_dspl_thr_psn_date, "YYYY/MM/DD"
        )
        self.dspl_thr_elev_source = to_nullable_string(dspl_thr_elev_source)
        self.rwy_end_dspl_thr_elev_date = to_nullable_date(
            rwy_end_dspl_thr_elev_date, "YYYY/MM/DD"
        )
        self.tkof_run_avbl = to_nullable_int(tkof_run_avbl)
        self.tkof_dist_avbl = to_nullable_int(tkof_dist_avbl)
        self.aclt_stop_dist_avbl = to_nullable_int(aclt_stop_dist_avbl)
        self.lndg_dist_avbl = to_nullable_int(lndg_dist_avbl)
        self.lahso_ald = to_nullable_int(lahso_ald)
        self.rwy_end_intersect_lahso = to_nullable_string(rwy_end_intersect_lahso)
        self.lahso_desc = to_nullable_string(lahso_desc)
        self.lahso_lat = to_nullable_string(lahso_lat)
        self.lat_lahso_decimal = to_nullable_float(lat_lahso_decimal)
        self.lahso_lon = to_nullable_string(lahso_lon)
        self.lon_lahso_decimal = to_nullable_float(lon_lahso_decimal)
        self.lahso_psn_source = to_nullable_string(lahso_psn_source)
        self.rwy_end_lahso_psn_date = to_nullable_date(
            rwy_end_lahso_psn_date, "YYYY/MM/DD"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"RWY_ID={self.rwy_id!r} ,"
            f"RWY_END_ID={self.rwy_end_id!r} ,"
            f"TRUE_ALIGNMENT={self.true_alignment!r} ,"
            f"ILS_TYPE={self.ils_type.value!r} ,"
            f"RIGHT_HAND_TRAFFIC_PAT_FLAG={self.right_hand_traffic_pat_flag!r} ,"
            f"RWY_MARKING_TYPE_CODE={self.rwy_marking_type_code.value!r} ,"
            f"RWY_MARKING_COND={self.rwy_marking_cond.value!r} ,"
            f"RWY_END_LAT_DEG={self.rwy_end_lat_deg!r} ,"
            f"RWY_END_LAT_MIN={self.rwy_end_lat_min!r} ,"
            f"RWY_END_LAT_SEC={self.rwy_end_lat_sec!r} ,"
            f"RWY_END_LAT_HEMIS={self.rwy_end_lat_hemis.value!r} ,"
            f"LAT_DECIMAL={self.lat_decimal!r} ,"
            f"RWY_END_LONG_DEG={self.rwy_end_lon_deg!r} ,"
            f"RWY_END_LONG_MIN={self.rwy_end_lon_min!r} ,"
            f"RWY_END_LONG_SEC={self.rwy_end_lon_sec!r} ,"
            f"RWY_END_LONG_HEMIS={self.rwy_end_lon_hemis.value!r} ,"
            f"LONG_DECIMAL={self.lon_decimal!r} ,"
            f"RWY_END_ELEV={self.rwy_end_elev!r} ,"
            f"THR_CROSSING_HGT={self.thr_crossing_hgt!r} ,"
            f"VISUAL_GLIDE_PATH_ANGLE={self.visual_glide_path_angle!r} ,"
            f"DISPLACED_THR_LAT_DEG={self.displaced_thr_lat_deg!r} ,"
            f"DISPLACED_THR_LAT_MIN={self.displaced_thr_lat_min!r} ,"
            f"DISPLACED_THR_LAT_SEC={self.displaced_thr_lat_sec!r} ,"
            f"DISPLACED_THR_LAT_HEMIS={self.displaced_thr_lat_hemis.value!r} ,"
            f"LAT_DISPLACED_THR_DECIMAL={self.lat_displaced_thr_decimal!r} ,"
            f"DISPLACED_THR_LONG_DEG={self.displaced_thr_lon_deg!r} ,"
            f"DISPLACED_THR_LONG_MIN={self.displaced_thr_lon_min!r} ,"
            f"DISPLACED_THR_LONG_SEC={self.displaced_thr_lon_sec!r} ,"
            f"DISPLACED_THR_LONG_HEMIS={self.displaced_thr_lon_hemis.value!r} ,"
            f"LONG_DISPLACED_THR_DECIMAL={self.lon_displaced_thr_decimal!r} ,"
            f"DISPLACED_THR_ELEV={self.displaced_thr_elev!r} ,"
            f"DISPLACED_THR_LEN={self.displaced_thr_len!r} ,"
            f"TDZ_ELEV={self.tdz_elev!r} ,"
            f"VGSI_CODE={self.vgsi_code.value!r} ,"
            f"RWY_VISUAL_RANGE_EQUIP_CODE={self.rwy_visual_range_equip_code.value!r} ,"
            f"RWY_VSBY_VALUE_EQUIP_FLAG={self.rwy_vsby_value_equip_flag!r} ,"
            f"APCH_LGT_SYSTEM_CODE={self.apch_lgt_system_code.value!r} ,"
            f"RWY_END_LGTS_FLAG={self.rwy_end_lgts_flag!r} ,"
            f"CNTRLN_LGTS_AVBL_FLAG={self.cntrln_lgts_avbl_flag!r} ,"
            f"TDZ_LGT_AVBL_FLAG={self.tdz_lgt_avbl_flag!r} ,"
            f"OBSTN_TYPE={self.obstn_type!r} ,"
            f"OBSTN_MRKD_CODE={self.obstn_mrkd_code.value!r} ,"
            f"FAR_PART_77_CODE={self.far_part_77_code.value!r} ,"
            f"OBSTN_CLNC_SLOPE={self.obstn_clnc_slope!r} ,"
            f"OBSTN_HGT={self.obstn_hgt!r} ,"
            f"DIST_FROM_THR={self.dist_from_thr!r} ,"
            f"CNTRLN_OFFSET={self.cntrln_offset!r} ,"
            f"CNTRLN_DIR_CODE={self.cntrln_dir_code!r} ,"
            f"RWY_GRAD={self.rwy_grad!r} ,"
            f"RWY_GRAD_DIRECTION={self.rwy_grad_direction!r} ,"
            f"RWY_END_PSN_SOURCE={self.rwy_end_psn_source!r} ,"
            f"RWY_END_PSN_DATE={self.rwy_end_psn_date!r} ,"
            f"RWY_END_ELEV_SOURCE={self.rwy_end_elev_source!r} ,"
            f"RWY_END_ELEV_DATE={self.rwy_end_elev_date!r} ,"
            f"DSPL_THR_PSN_SOURCE={self.dspl_thr_psn_source!r} ,"
            f"RWY_END_DSPL_THR_PSN_DATE={self.rwy_end_dspl_thr_psn_date!r} ,"
            f"DSPL_THR_ELEV_SOURCE={self.dspl_thr_elev_source!r} ,"
            f"RWY_END_DSPL_THR_ELEV_DATE={self.rwy_end_dspl_thr_elev_date!r} ,"
            f"TKOF_RUN_AVBL={self.tkof_run_avbl!r} ,"
            f"TKOF_DIST_AVBL={self.tkof_dist_avbl!r} ,"
            f"ACLT_STOP_DIST_AVBL={self.aclt_stop_dist_avbl!r} ,"
            f"LNDG_DIST_AVBL={self.lndg_dist_avbl!r} ,"
            f"LAHSO_ALD={self.lahso_ald!r} ,"
            f"RWY_END_INTERSECT_LAHSO={self.rwy_end_intersect_lahso!r} ,"
            f"LAHSO_DESC={self.lahso_desc!r} ,"
            f"LAHSO_LAT={self.lahso_lat!r} ,"
            f"LAT_LAHSO_DECIMAL={self.lat_lahso_decimal!r} ,"
            f"LAHSO_LONG={self.lahso_lon!r} ,"
            f"LONG_LAHSO_DECIMAL={self.lon_lahso_decimal!r} ,"
            f"LAHSO_PSN_SOURCE={self.lahso_psn_source!r} ,"
            f"RWY_END_LAHSO_PSN_DATE={self.rwy_end_lahso_psn_date!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "rwy_id",
                "rwy_end_id",
                "true_alignment",
                "ils_type",
                "right_hand_traffic_pat_flag",
                "rwy_marking_type_code",
                "rwy_marking_cond",
                "rwy_end_lat_deg",
                "rwy_end_lat_min",
                "rwy_end_lat_sec",
                "rwy_end_lat_hemis",
                "lat_decimal",
                "rwy_end_lon_deg",
                "rwy_end_lon_min",
                "rwy_end_lon_sec",
                "rwy_end_lon_hemis",
                "lon_decimal",
                "rwy_end_elev",
                "thr_crossing_hgt",
                "visual_glide_path_angle",
                "displaced_thr_lat_deg",
                "displaced_thr_lat_min",
                "displaced_thr_lat_sec",
                "displaced_thr_lat_hemis",
                "lat_displaced_thr_decimal",
                "displaced_thr_lon_deg",
                "displaced_thr_lon_min",
                "displaced_thr_lon_sec",
                "displaced_thr_lon_hemis",
                "lon_displaced_thr_decimal",
                "displaced_thr_elev",
                "displaced_thr_len",
                "tdz_elev",
                "vgsi_code",
                "rwy_visual_range_equip_code",
                "rwy_vsby_value_equip_flag",
                "apch_lgt_system_code",
                "rwy_end_lgts_flag",
                "cntrln_lgts_avbl_flag",
                "tdz_lgt_avbl_flag",
                "obstn_type",
                "obstn_mrkd_code",
                "far_part_77_code",
                "obstn_clnc_slope",
                "obstn_hgt",
                "dist_from_thr",
                "cntrln_offset",
                "cntrln_dir_code",
                "rwy_grad",
                "rwy_grad_direction",
                "rwy_end_psn_source",
                "rwy_end_psn_date",
                "rwy_end_elev_source",
                "rwy_end_elev_date",
                "dspl_thr_psn_source",
                "rwy_end_dspl_thr_psn_date",
                "dspl_thr_elev_source",
                "rwy_end_dspl_thr_elev_date",
                "tkof_run_avbl",
                "tkof_dist_avbl",
                "aclt_stop_dist_avbl",
                "lndg_dist_avbl",
                "lahso_ald",
                "rwy_end_intersect_lahso",
                "lahso_desc",
                "lahso_lat",
                "lat_lahso_decimal",
                "lahso_lon",
                "lon_lahso_decimal",
                "lahso_psn_source",
                "rwy_end_lahso_psn_date",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "rwy_id": self.rwy_id,
            "rwy_end_id": self.rwy_end_id,
            "true_alignment": self.true_alignment,
            "ils_type": self.ils_type.value,
            "right_hand_traffic_pat_flag": self.right_hand_traffic_pat_flag,
            "rwy_marking_type_code": self.rwy_marking_type_code.value,
            "rwy_marking_cond": self.rwy_marking_cond.value,
            "rwy_end_lat_deg": self.rwy_end_lat_deg,
            "rwy_end_lat_min": self.rwy_end_lat_min,
            "rwy_end_lat_sec": self.rwy_end_lat_sec,
            "rwy_end_lat_hemis": self.rwy_end_lat_hemis.value,
            "lat_decimal": self.lat_decimal,
            "rwy_end_lon_deg": self.rwy_end_lon_deg,
            "rwy_end_lon_min": self.rwy_end_lon_min,
            "rwy_end_lon_sec": self.rwy_end_lon_sec,
            "rwy_end_lon_hemis": self.rwy_end_lon_hemis.value,
            "lon_decimal": self.lon_decimal,
            "rwy_end_elev": self.rwy_end_elev,
            "thr_crossing_hgt": self.thr_crossing_hgt,
            "visual_glide_path_angle": self.visual_glide_path_angle,
            "displaced_thr_lat_deg": self.displaced_thr_lat_deg,
            "displaced_thr_lat_min": self.displaced_thr_lat_min,
            "displaced_thr_lat_sec": self.displaced_thr_lat_sec,
            "displaced_thr_lat_hemis": self.displaced_thr_lat_hemis.value,
            "lat_displaced_thr_decimal": self.lat_displaced_thr_decimal,
            "displaced_thr_lon_deg": self.displaced_thr_lon_deg,
            "displaced_thr_lon_min": self.displaced_thr_lon_min,
            "displaced_thr_lon_sec": self.displaced_thr_lon_sec,
            "displaced_thr_lon_hemis": self.displaced_thr_lon_hemis.value,
            "lon_displaced_thr_decimal": self.lon_displaced_thr_decimal,
            "displaced_thr_elev": self.displaced_thr_elev,
            "displaced_thr_len": self.displaced_thr_len,
            "tdz_elev": self.tdz_elev,
            "vgsi_code": self.vgsi_code.value,
            "rwy_visual_range_equip_code": self.rwy_visual_range_equip_code.value,
            "rwy_vsby_value_equip_flag": self.rwy_vsby_value_equip_flag,
            "apch_lgt_system_code": self.apch_lgt_system_code.value,
            "rwy_end_lgts_flag": self.rwy_end_lgts_flag,
            "cntrln_lgts_avbl_flag": self.cntrln_lgts_avbl_flag,
            "tdz_lgt_avbl_flag": self.tdz_lgt_avbl_flag,
            "obstn_type": self.obstn_type,
            "obstn_mrkd_code": self.obstn_mrkd_code.value,
            "far_part_77_code": self.far_part_77_code.value,
            "obstn_clnc_slope": self.obstn_clnc_slope,
            "obstn_hgt": self.obstn_hgt,
            "dist_from_thr": self.dist_from_thr,
            "cntrln_offset": self.cntrln_offset,
            "cntrln_dir_code": self.cntrln_dir_code,
            "rwy_grad": self.rwy_grad,
            "rwy_grad_direction": self.rwy_grad_direction,
            "rwy_end_psn_source": self.rwy_end_psn_source,
            "rwy_end_psn_date": self.rwy_end_psn_date,
            "rwy_end_elev_source": self.rwy_end_elev_source,
            "rwy_end_elev_date": self.rwy_end_elev_date,
            "dspl_thr_psn_source": self.dspl_thr_psn_source,
            "rwy_end_dspl_thr_psn_date": self.rwy_end_dspl_thr_psn_date,
            "dspl_thr_elev_source": self.dspl_thr_elev_source,
            "rwy_end_dspl_thr_elev_date": self.rwy_end_dspl_thr_elev_date,
            "tkof_run_avbl": self.tkof_run_avbl,
            "tkof_dist_avbl": self.tkof_dist_avbl,
            "aclt_stop_dist_avbl": self.aclt_stop_dist_avbl,
            "lndg_dist_avbl": self.lndg_dist_avbl,
            "lahso_ald": self.lahso_ald,
            "rwy_end_intersect_lahso": self.rwy_end_intersect_lahso,
            "lahso_desc": self.lahso_desc,
            "lahso_lat": self.lahso_lat,
            "lat_lahso_decimal": self.lat_lahso_decimal,
            "lahso_lon": self.lahso_lon,
            "lon_lahso_decimal": self.lon_lahso_decimal,
            "lahso_psn_source": self.lahso_psn_source,
            "rwy_end_lahso_psn_date": self.rwy_end_lahso_psn_date,
        }
        return {**base_dict, **this_dict}
