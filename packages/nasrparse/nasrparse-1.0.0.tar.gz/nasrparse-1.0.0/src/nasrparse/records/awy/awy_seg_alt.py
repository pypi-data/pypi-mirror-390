from nasrparse.functions import (
    to_nullable_bool,
    to_nullable_float,
    to_nullable_int,
    to_nullable_string,
)
from nasrparse.records.types import PointCode

from ._base import Base


class AWY_SEG_ALT(Base):
    point_seq: int | None
    """Sequencing number in multiples of ten. Points are in order adapted for given Airway."""
    from_point: str | None
    """NAVAID Facility Identifier, FIX Name or Border crossing. A Unique system generated number is added to each Border crossing Segment Value. This number while unique is not necessarily sequential."""
    from_pt_type: PointCode
    """NAVAID Facility or FIX Type."""
    nav_name: str | None
    """NAVAID Facility Name"""
    nav_city: str | None
    """The NAVIAD Facility City which is part of the key for all NAV_*.csv files."""
    artcc: str | None
    """Identifier of Low ARTCC Altitude Boundary That the FROM_POINT FIX/NAVAID Falls Within."""
    icao_region_code: str | None
    """This is the two letter ICAO Region Code for FIX Point Types only."""
    state_code: str | None
    """Associated State Post Office Code standard two letter abbreviation for US States and Territories."""
    country_code: str | None
    """Country Post Office Code"""
    to_point: str | None
    """The To Point that directly follows the current From Point on an individual segment."""
    mag_course: float | None
    """Segment Magnetic Course"""
    opp_mag_course: float | None
    """Segment Magnetic Course - Opposite Direction"""
    mag_course_dist: float | None
    """Distance to Next Point in Segment in Nautical Miles."""
    chgovr_pt: str | None
    """NAVAID Changeover Point Facility Identifier"""
    chgovr_pt_name: str | None
    """NAVAID Changeover Point Facility Name"""
    chgovr_pt_dist: float | None
    """This Field Contains The Distance In Nautical Miles Of The Changeover Point Between This NAVAID Facility And The Next NAVAID Facility When The Changeover Point Is More Than One Mile From Half-Way Point."""
    awy_seg_gap_flag: bool | None
    """Airway Gap Flag Indicator for when Airway Discontinued - Y/N."""
    signal_gap_flag: bool | None
    """Gap in Signal Coverage Indicator for when Mea established With a Gap in Navigation Signal Coverage - Y/N."""
    dogleg: bool | None
    """A Turn Point Not At A NAVAID - Y/N. Note: GPS RNAV Routes [Q, T, TK] will have Dogleg=Y at First Point, End Point, And All Turn Points in between."""
    next_mea_pt: str | None
    """The To MEA_PT that directly follows the From MEA_PT for an individual Altitude record."""
    min_enroute_alt: int | None
    """Point To Point Minimum Enroute Altitude (MEA)"""
    min_enroute_alt_dir: str | None
    """Point To Point Minimum Enroute Direction (MEA)"""
    min_enroute_alt_opposite: int | None
    """Point To Point Minimum Enroute Altitude (MEA-Opposite Direction)"""
    min_enroute_alt_opposite_dir: str | None
    """Point To Point Minimum Enroute Direction (MEA-Opposite Direction)"""
    gps_min_enroute_alt: int | None
    """Point To Point GNSS Minimum Enroute Altitude (Global Navigation Satellite System MEA)"""
    gps_min_enroute_alt_dir: str | None
    """Point To Point GNSS Minimum Enroute Direction (Global Navigation Satellite System MEA)"""
    gps_min_enroute_alt_opposite: int | None
    """Point To Point GNSS Minimum Enroute Altitude (Global Navigation Satellite System MEA-Opposite Direction)"""
    gps_mea_opposite_dir: str | None
    """Point To Point GNSS Minimum Enroute Direction (Global Navigation Satellite System MEA-Opposite Direction)"""
    dd_iru_mea: int | None
    """Point To Point DME/DME/IRU Minimum Enroute Altitude (MEA)"""
    dd_iru_mea_dir: str | None
    """Point To Point DME/DME/IRU Minimum Enroute Direction (MEA)"""
    dd_i_mea_opposite: int | None
    """Point To Point DME/DME/IRU Minimum Enroute Altitude (MEA- Opposite Direction)"""
    dd_i_mea_opposite_dir: str | None
    """Point To Point DME/DME/IRU Minimum Enroute Direction (MEA- Opposite Direction)"""
    min_obstn_clnc_alt: int | None
    """Point To Point Minimum Obstruction Clearance Altitude (MOCA)"""
    min_cross_alt: int | None
    """Minimum Crossing Altitude (MCA)"""
    min_cross_alt_dir: str | None
    """Minimum Crossing Direction (MCA)"""
    min_cross_alt_nav_pt: str | None
    """Minimum Crossing Altitude (MCA) Point"""
    min_cross_alt_opposite: int | None
    """Minimum Crossing Altitude (MCA- Opposite Direction)"""
    min_cross_alt_opposite_dir: str | None
    """Minimum Crossing Direction (MCA- Opposite Direction)"""
    min_recep_alt: int | None
    """FIX Minimum Reception Altitude (MRA)"""
    max_auth_alt: int | None
    """Point To Point Maximum Authorized Altitude (MAA)"""
    mea_gap: str | None
    """Identifies whether a given MEA Segment is Unusable - “U”."""
    reqd_nav_performance: str | None
    """Required Navigation Performance (RNP) value."""
    remark: str | None
    """Remark Text (Free Form Text that further describes a specific Information Item.)"""

    def __init__(
        self,
        eff_date: str,
        regulatory: str,
        awy_location: str,
        awy_id: str,
        point_seq: str,
        from_point: str,
        from_pt_type: str,
        nav_name: str,
        nav_city: str,
        artcc: str,
        icao_region_code: str,
        state_code: str,
        country_code: str,
        to_point: str,
        mag_course: str,
        opp_mag_course: str,
        mag_course_dist: str,
        chgovr_pt: str,
        chgovr_pt_name: str,
        chgovr_pt_dist: str,
        awy_seg_gap_flag: str,
        signal_gap_flag: str,
        dogleg: str,
        next_mea_pt: str,
        min_enroute_alt: str,
        min_enroute_alt_dir: str,
        min_enroute_alt_opposite: str,
        min_enroute_alt_opposite_dir: str,
        gps_min_enroute_alt: str,
        gps_min_enroute_alt_dir: str,
        gps_min_enroute_alt_opposite: str,
        gps_mea_opposite_dir: str,
        dd_iru_mea: str,
        dd_iru_mea_dir: str,
        dd_i_mea_opposite: str,
        dd_i_mea_opposite_dir: str,
        min_obstn_clnc_alt: str,
        min_cross_alt: str,
        min_cross_alt_dir: str,
        min_cross_alt_nav_pt: str,
        min_cross_alt_opposite: str,
        min_cross_alt_opposite_dir: str,
        min_recep_alt: str,
        max_auth_alt: str,
        mea_gap: str,
        reqd_nav_performance: str,
        remark: str,
    ) -> None:
        super().__init__(
            "airway_segments",
            eff_date,
            regulatory,
            awy_location,
            awy_id,
        )
        self.point_seq = to_nullable_int(point_seq)
        self.from_point = to_nullable_string(from_point)
        self.from_pt_type = PointCode.from_value(to_nullable_string(from_pt_type))
        self.nav_name = to_nullable_string(nav_name)
        self.nav_city = to_nullable_string(nav_city)
        self.artcc = to_nullable_string(artcc)
        self.icao_region_code = to_nullable_string(icao_region_code)
        self.state_code = to_nullable_string(state_code)
        self.country_code = to_nullable_string(country_code)
        self.to_point = to_nullable_string(to_point)
        self.mag_course = to_nullable_float(mag_course)
        self.opp_mag_course = to_nullable_float(opp_mag_course)
        self.mag_course_dist = to_nullable_float(mag_course_dist)
        self.chgovr_pt = to_nullable_string(chgovr_pt)
        self.chgovr_pt_name = to_nullable_string(chgovr_pt_name)
        self.chgovr_pt_dist = to_nullable_float(chgovr_pt_dist)
        self.awy_seg_gap_flag = to_nullable_bool(awy_seg_gap_flag)
        self.signal_gap_flag = to_nullable_bool(signal_gap_flag)
        self.dogleg = to_nullable_bool(dogleg)
        self.next_mea_pt = to_nullable_string(next_mea_pt)
        self.min_enroute_alt = to_nullable_int(min_enroute_alt)
        self.min_enroute_alt_dir = to_nullable_string(min_enroute_alt_dir)
        self.min_enroute_alt_opposite = to_nullable_int(min_enroute_alt_opposite)
        self.min_enroute_alt_opposite_dir = to_nullable_string(
            min_enroute_alt_opposite_dir
        )
        self.gps_min_enroute_alt = to_nullable_int(gps_min_enroute_alt)
        self.gps_min_enroute_alt_dir = to_nullable_string(gps_min_enroute_alt_dir)
        self.gps_min_enroute_alt_opposite = to_nullable_int(
            gps_min_enroute_alt_opposite
        )
        self.gps_mea_opposite_dir = to_nullable_string(gps_mea_opposite_dir)
        self.dd_iru_mea = to_nullable_int(dd_iru_mea)
        self.dd_iru_mea_dir = to_nullable_string(dd_iru_mea_dir)
        self.dd_i_mea_opposite = to_nullable_int(dd_i_mea_opposite)
        self.dd_i_mea_opposite_dir = to_nullable_string(dd_i_mea_opposite_dir)
        self.min_obstn_clnc_alt = to_nullable_int(min_obstn_clnc_alt)
        self.min_cross_alt = to_nullable_int(min_cross_alt)
        self.min_cross_alt_dir = to_nullable_string(min_cross_alt_dir)
        self.min_cross_alt_nav_pt = to_nullable_string(min_cross_alt_nav_pt)
        self.min_cross_alt_opposite = to_nullable_int(min_cross_alt_opposite)
        self.min_cross_alt_opposite_dir = to_nullable_string(min_cross_alt_opposite_dir)
        self.min_recep_alt = to_nullable_int(min_recep_alt)
        self.max_auth_alt = to_nullable_int(max_auth_alt)
        self.mea_gap = to_nullable_string(mea_gap)
        self.reqd_nav_performance = to_nullable_string(reqd_nav_performance)
        self.remark = to_nullable_string(remark)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"POINT_SEQ={self.point_seq}, "
            f"FROM_POINT={self.from_point}, "
            f"FROM_PT_TYPE={self.from_pt_type}, "
            f"NAV_NAME={self.nav_name}, "
            f"NAV_CITY={self.nav_city}, "
            f"ARTCC={self.artcc}, "
            f"ICAO_REGION_CODE={self.icao_region_code}, "
            f"STATE_CODE={self.state_code}, "
            f"COUNTRY_CODE={self.country_code}, "
            f"TO_POINT={self.to_point}, "
            f"MAG_COURSE={self.mag_course}, "
            f"OPP_MAG_COURSE={self.opp_mag_course}, "
            f"MAG_COURSE_DIST={self.mag_course_dist}, "
            f"CHGOVR_PT={self.chgovr_pt}, "
            f"CHGOVR_PT_NAME={self.chgovr_pt_name}, "
            f"CHGOVR_PT_DIST={self.chgovr_pt_dist}, "
            f"AWY_SEG_GAP_FLAG={self.awy_seg_gap_flag}, "
            f"SIGNAL_GAP_FLAG={self.signal_gap_flag}, "
            f"DOGLEG={self.dogleg}, "
            f"NEXT_MEA_PT={self.next_mea_pt}, "
            f"MIN_ENROUTE_ALT={self.min_enroute_alt}, "
            f"MIN_ENROUTE_ALT_DIR={self.min_enroute_alt_dir}, "
            f"MIN_ENROUTE_ALT_OPPOSITE={self.min_enroute_alt_opposite}, "
            f"MIN_ENROUTE_ALT_OPPOSITE_DIR={self.min_enroute_alt_opposite_dir}, "
            f"GPS_MIN_ENROUTE_ALT={self.gps_min_enroute_alt}, "
            f"GPS_MIN_ENROUTE_ALT_DIR={self.gps_min_enroute_alt_dir}, "
            f"GPS_MIN_ENROUTE_ALT_OPPOSITE={self.gps_min_enroute_alt_opposite}, "
            f"GPS_MEA_OPPOSITE_DIR={self.gps_mea_opposite_dir}, "
            f"DD_IRU_MEA={self.dd_iru_mea}, "
            f"DD_IRU_MEA_DIR={self.dd_iru_mea_dir}, "
            f"DD_I_MEA_OPPOSITE={self.dd_i_mea_opposite}, "
            f"DD_I_MEA_OPPOSITE_DIR={self.dd_i_mea_opposite_dir}, "
            f"MIN_OBSTN_CLNC_ALT={self.min_obstn_clnc_alt}, "
            f"MIN_CROSS_ALT={self.min_cross_alt}, "
            f"MIN_CROSS_ALT_DIR={self.min_cross_alt_dir}, "
            f"MIN_CROSS_ALT_NAV_PT={self.min_cross_alt_nav_pt}, "
            f"MIN_CROSS_ALT_OPPOSITE={self.min_cross_alt_opposite}, "
            f"MIN_CROSS_ALT_OPPOSITE_DIR={self.min_cross_alt_opposite_dir}, "
            f"MIN_RECEP_ALT={self.min_recep_alt}, "
            f"MAX_AUTH_ALT={self.max_auth_alt}, "
            f"MEA_GAP={self.mea_gap}, "
            f"REQD_NAV_PERFORMANCE={self.reqd_nav_performance}, "
            f"REMARK={self.remark}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "point_seq",
                "from_point",
                "from_pt_type",
                "nav_name",
                "nav_city",
                "artcc",
                "icao_region_code",
                "state_code",
                "country_code",
                "to_point",
                "mag_course",
                "opp_mag_course",
                "mag_course_dist",
                "chgovr_pt",
                "chgovr_pt_name",
                "chgovr_pt_dist",
                "awy_seg_gap_flag",
                "signal_gap_flag",
                "dogleg",
                "next_mea_pt",
                "min_enroute_alt",
                "min_enroute_alt_dir",
                "min_enroute_alt_opposite",
                "min_enroute_alt_opposite_dir",
                "gps_min_enroute_alt",
                "gps_min_enroute_alt_dir",
                "gps_min_enroute_alt_opposite",
                "gps_mea_opposite_dir",
                "dd_iru_mea",
                "dd_iru_mea_dir",
                "dd_i_mea_opposite",
                "dd_i_mea_opposite_dir",
                "min_obstn_clnc_alt",
                "min_cross_alt",
                "min_cross_alt_dir",
                "min_cross_alt_nav_pt",
                "min_cross_alt_opposite",
                "min_cross_alt_opposite_dir",
                "min_recep_alt",
                "max_auth_alt",
                "mea_gap",
                "reqd_nav_performance",
                "remark",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "point_seq": self.point_seq,
            "from_point": self.from_point,
            "from_pt_type": self.from_pt_type.value if self.from_pt_type else None,
            "nav_name": self.nav_name,
            "nav_city": self.nav_city,
            "artcc": self.artcc,
            "icao_region_code": self.icao_region_code,
            "state_code": self.state_code,
            "country_code": self.country_code,
            "to_point": self.to_point,
            "mag_course": self.mag_course,
            "opp_mag_course": self.opp_mag_course,
            "mag_course_dist": self.mag_course_dist,
            "chgovr_pt": self.chgovr_pt,
            "chgovr_pt_name": self.chgovr_pt_name,
            "chgovr_pt_dist": self.chgovr_pt_dist,
            "awy_seg_gap_flag": self.awy_seg_gap_flag,
            "signal_gap_flag": self.signal_gap_flag,
            "dogleg": self.dogleg,
            "next_mea_pt": self.next_mea_pt,
            "min_enroute_alt": self.min_enroute_alt,
            "min_enroute_alt_dir": self.min_enroute_alt_dir,
            "min_enroute_alt_opposite": self.min_enroute_alt_opposite,
            "min_enroute_alt_opposite_dir": self.min_enroute_alt_opposite_dir,
            "gps_min_enroute_alt": self.gps_min_enroute_alt,
            "gps_min_enroute_alt_dir": self.gps_min_enroute_alt_dir,
            "gps_min_enroute_alt_opposite": self.gps_min_enroute_alt_opposite,
            "gps_mea_opposite_dir": self.gps_mea_opposite_dir,
            "dd_iru_mea": self.dd_iru_mea,
            "dd_iru_mea_dir": self.dd_iru_mea_dir,
            "dd_i_mea_opposite": self.dd_i_mea_opposite,
            "dd_i_mea_opposite_dir": self.dd_i_mea_opposite_dir,
            "min_obstn_clnc_alt": self.min_obstn_clnc_alt,
            "min_cross_alt": self.min_cross_alt,
            "min_cross_alt_dir": self.min_cross_alt_dir,
            "min_cross_alt_nav_pt": self.min_cross_alt_nav_pt,
            "min_cross_alt_opposite": self.min_cross_alt_opposite,
            "min_cross_alt_opposite_dir": self.min_cross_alt_opposite_dir,
            "min_recep_alt": self.min_recep_alt,
            "max_auth_alt": self.max_auth_alt,
            "mea_gap": self.mea_gap,
            "reqd_nav_performance": self.reqd_nav_performance,
            "remark": self.remark,
        }
        return {**base_dict, **this_dict}
