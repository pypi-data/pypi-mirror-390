from nasrparse.functions import to_nullable_int, to_nullable_string
from nasrparse.records.types import PointCode

from ._base import Base


class AWY_ALT(Base):
    point_seq: int | None
    """POINT_SEQ Number from the AWY_SEG file."""
    mea_pt: str | None
    """NAVAID Facility Identifier, FIX Name or Border crossing associated with POINT_SEQ. A Unique system generated number is added to each Border crossing Segment Value. This number while unique is not necessarily sequential."""
    mea_pt_type: PointCode
    """NAVAID Facility or FIX Type of MEA_PT. (see SEQ_TYPE for list)"""
    nav_name: str | None
    """NAVAID Facility Name"""
    nav_city: str | None
    """The NAVIAD Facility City which is part of the key for all NAV_*.csv files."""
    icao_region_code: str | None
    """This is the two letter ICAO Region Code for FIX Point Types only."""
    state_code: str | None
    """Associated State Post Office Code standard two-letter abbreviation for US States and Territories."""
    country_code: str | None
    """Country Post Office Code"""
    next_mea_pt: int | None
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
        mea_pt: str,
        mea_pt_type: str,
        nav_name: str,
        nav_city: str,
        icao_region_code: str,
        state_code: str,
        country_code: str,
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
        self.mea_pt = to_nullable_string(mea_pt)
        self.mea_pt_type = PointCode.from_value(to_nullable_string(mea_pt_type))
        self.nav_name = to_nullable_string(nav_name)
        self.nav_city = to_nullable_string(nav_city)
        self.icao_region_code = to_nullable_string(icao_region_code)
        self.state_code = to_nullable_string(state_code)
        self.country_code = to_nullable_string(country_code)
        self.next_mea_pt = to_nullable_int(next_mea_pt)
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
            f"POINT_SEQ={self.point_seq!r}, "
            f"MEA_PT={self.mea_pt!r}, "
            f"MEA_PT_TYPE={self.mea_pt_type!r}, "
            f"NAV_NAME={self.nav_name!r}, "
            f"NAV_CITY={self.nav_city!r}, "
            f"ICAO_REGION_CODE={self.icao_region_code!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"COUNTRY_CODE={self.country_code!r}, "
            f"NEXT_MEA_PT={self.next_mea_pt!r}, "
            f"MIN_ENROUTE_ALT={self.min_enroute_alt!r}, "
            f"MIN_ENROUTE_ALT_DIR={self.min_enroute_alt_dir!r}, "
            f"MIN_ENROUTE_ALT_OPPOSITE={self.min_enroute_alt_opposite!r}, "
            f"MIN_ENROUTE_ALT_OPPOSITE_DIR={self.min_enroute_alt_opposite_dir!r}, "
            f"GPS_MIN_ENROUTE_ALT={self.gps_min_enroute_alt!r}, "
            f"GPS_MIN_ENROUTE_ALT_DIR={self.gps_min_enroute_alt_dir!r}, "
            f"GPS_MIN_ENROUTE_ALT_OPPOSITE={self.gps_min_enroute_alt_opposite!r}, "
            f"GPS_MEA_OPPOSITE_DIR={self.gps_mea_opposite_dir!r}, "
            f"DD_IRU_MEA={self.dd_iru_mea!r}, "
            f"DD_IRU_MEA_DIR={self.dd_iru_mea_dir!r}, "
            f"DD_I_MEA_OPPOSITE={self.dd_i_mea_opposite!r}, "
            f"DD_I_MEA_OPPOSITE_DIR={self.dd_i_mea_opposite_dir!r}, "
            f"MIN_OBSTN_CLNC_ALT={self.min_obstn_clnc_alt!r}, "
            f"MIN_CROSS_ALT={self.min_cross_alt!r}, "
            f"MIN_CROSS_ALT_DIR={self.min_cross_alt_dir!r}, "
            f"MIN_CROSS_ALT_NAV_PT={self.min_cross_alt_nav_pt!r}, "
            f"MIN_CROSS_ALT_OPPOSITE={self.min_cross_alt_opposite!r}, "
            f"MIN_CROSS_ALT_OPPOSITE_DIR={self.min_cross_alt_opposite_dir!r}, "
            f"MIN_RECEP_ALT={self.min_recep_alt!r}, "
            f"MAX_AUTH_ALT={self.max_auth_alt!r}, "
            f"MEA_GAP={self.mea_gap!r}, "
            f"REQD_NAV_PERFORMANCE={self.reqd_nav_performance!r}, "
            f"REMARK={self.remark!r}, "
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "point_seq",
                "mea_pt",
                "mea_pt_type",
                "nav_name",
                "nav_city",
                "icao_region_code",
                "state_code",
                "country_code",
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
            "mea_pt": self.mea_pt,
            "mea_pt_type": self.mea_pt_type.value if self.mea_pt_type else None,
            "nav_name": self.nav_name,
            "nav_city": self.nav_city,
            "icao_region_code": self.icao_region_code,
            "state_code": self.state_code,
            "country_code": self.country_code,
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
