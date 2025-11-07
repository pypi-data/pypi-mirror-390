from nasrparse.functions import (
    to_nullable_bool,
    to_nullable_float,
    to_nullable_int,
    to_nullable_string,
)

from ._base import Base


class AWY_SEG(Base):
    point_seq: int | None
    """Sequencing number in multiples of ten. Points are in order adapted for given Airway."""
    seg_value: str | None
    """NAVAID Facility Identifier, FIX Name or Border crossing. A Unique system generated number is added to each Border crossing Segment Value. This number while unique is not necessarily sequential."""
    seg_type: str | None
    """NAVAID Facility or FIX Type."""
    nav_name: str | None
    """NAVAID Facility Name"""
    nav_city: str | None
    """The NAVIAD Facility City which is part of the key for all NAV_*.csv files."""
    icao_region_code: str | None
    """This is the two letter ICAO Region Code for FIX Point Types only."""
    state_code: str | None
    """Associated State Post Office Code standard two letter abbreviation for US States and Territories."""
    country_code: str | None
    """Country Post Office Code"""
    next_seg: str | None
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
    remark: str | None
    """Remark Text (Free Form Text that further describes a specific Information Item.)"""

    def __init__(
        self,
        eff_date: str,
        regulatory: str,
        awy_location: str,
        awy_id: str,
        point_seq: str,
        seg_value: str,
        seg_type: str,
        nav_name: str,
        nav_city: str,
        icao_region_code: str,
        state_code: str,
        country_code: str,
        next_seg: str,
        mag_course: str,
        opp_mag_course: str,
        mag_course_dist: str,
        chgovr_pt: str,
        chgovr_pt_name: str,
        chgovr_pt_dist: str,
        awy_seg_gap_flag: str,
        signal_gap_flag: str,
        dogleg: str,
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
        self.seg_value = to_nullable_string(seg_value)
        self.seg_type = to_nullable_string(seg_type)
        self.nav_name = to_nullable_string(nav_name)
        self.nav_city = to_nullable_string(nav_city)
        self.icao_region_code = to_nullable_string(icao_region_code)
        self.state_code = to_nullable_string(state_code)
        self.country_code = to_nullable_string(country_code)
        self.next_seg = to_nullable_string(next_seg)
        self.mag_course = to_nullable_float(mag_course)
        self.opp_mag_course = to_nullable_float(opp_mag_course)
        self.mag_course_dist = to_nullable_float(mag_course_dist)
        self.chgovr_pt = to_nullable_string(chgovr_pt)
        self.chgovr_pt_name = to_nullable_string(chgovr_pt_name)
        self.chgovr_pt_dist = to_nullable_float(chgovr_pt_dist)
        self.awy_seg_gap_flag = to_nullable_bool(awy_seg_gap_flag)
        self.signal_gap_flag = to_nullable_bool(signal_gap_flag)
        self.dogleg = to_nullable_bool(dogleg)
        self.remark = to_nullable_string(remark)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"POINT_SEQ={self.point_seq!r}, "
            f"SEG_VALUE={self.seg_value!r}, "
            f"SEG_TYPE={self.seg_type!r}, "
            f"NAV_NAME={self.nav_name!r}, "
            f"NAV_CITY={self.nav_city!r}, "
            f"ICAO_REGION_CODE={self.icao_region_code!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"COUNTRY_CODE={self.country_code!r}, "
            f"NEXT_SEG={self.next_seg!r}, "
            f"MAG_COURSE={self.mag_course!r}, "
            f"OPP_MAG_COURSE={self.opp_mag_course!r}, "
            f"MAG_COURSE_DIST={self.mag_course_dist!r}, "
            f"CHGOVR_PT={self.chgovr_pt!r}, "
            f"CHGOVR_PT_NAME={self.chgovr_pt_name!r}, "
            f"CHGOVR_PT_DIST={self.chgovr_pt_dist!r}, "
            f"AWY_SEG_GAP_FLAG={self.awy_seg_gap_flag!r}, "
            f"SIGNAL_GAP_FLAG={self.signal_gap_flag!r}, "
            f"DOGLEG={self.dogleg!r}, "
            f"REMARK={self.remark!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "point_seq",
                "seg_value",
                "seg_type",
                "nav_name",
                "nav_city",
                "icao_region_code",
                "state_code",
                "country_code",
                "next_seg",
                "mag_course",
                "opp_mag_course",
                "mag_course_dist",
                "chgovr_pt",
                "chgovr_pt_name",
                "chgovr_pt_dist",
                "awy_seg_gap_flag",
                "signal_gap_flag",
                "dogleg",
                "remark",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "point_seq": self.point_seq,
            "seg_value": self.seg_value,
            "seg_type": self.seg_type,
            "nav_name": self.nav_name,
            "nav_city": self.nav_city,
            "icao_region_code": self.icao_region_code,
            "state_code": self.state_code,
            "country_code": self.country_code,
            "next_seg": self.next_seg,
            "mag_course": self.mag_course,
            "opp_mag_course": self.opp_mag_course,
            "mag_course_dist": self.mag_course_dist,
            "chgovr_pt": self.chgovr_pt,
            "chgovr_pt_name": self.chgovr_pt_name,
            "chgovr_pt_dist": self.chgovr_pt_dist,
            "awy_seg_gap_flag": self.awy_seg_gap_flag,
            "signal_gap_flag": self.signal_gap_flag,
            "dogleg": self.dogleg,
            "remark": self.remark,
        }
        return {**base_dict, **this_dict}
