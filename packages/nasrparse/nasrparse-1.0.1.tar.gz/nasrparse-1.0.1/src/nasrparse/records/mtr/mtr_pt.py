from nasrparse.functions import to_nullable_float, to_nullable_int, to_nullable_string
from nasrparse.records.types import HemisCode

from ._base import Base


class MTR_PT(Base):
    route_pt_seq: int | None
    """Sequencing number in multiples of ten. Points are in order adapted for given MTR."""
    route_pt_id: str | None
    """Route Point Identifier."""
    next_route_pt_id: str | None
    """The Next Sequential ROUTE_PT_ID."""
    segment_text: str | None
    """Concatenation of Segment Text preceded by the Segment Text Sequence Number."""
    lat_deg: int | None
    """MTR Route Point Latitude Degrees"""
    lat_min: int | None
    """MTR Route Point Latitude Minutes"""
    lat_sec: float | None
    """MTR Route Point Latitude Seconds"""
    lat_hemis: HemisCode
    """MTR Route Point Latitude Hemisphere"""
    lat_decimal: float | None
    """MTR Route Point Latitude in Decimal Format"""
    lon_deg: int | None
    """MTR Route Point Longitude Degrees"""
    lon_min: int | None
    """MTR Route Point Longitude Minutes"""
    lon_sec: float | None
    """MTR Route Point Longitude Seconds"""
    lon_hemis: HemisCode
    """MTR Route Point Longitude Hemisphere"""
    lon_decimal: float | None
    """MTR Route Point Longitude in Decimal Format"""
    nav_id: str | None
    """Identifier of related NAVAID"""
    navaid_bearing: float | None
    """Bearing of NAVAID from Point"""
    navaid_dist: float | None
    """Distance of NAVAID from Point"""

    def __init__(
        self,
        eff_date: str,
        route_type_code: str,
        route_id: str,
        artcc: str,
        route_pt_seq: str,
        route_pt_id: str,
        next_route_pt_id: str,
        segment_text: str,
        lat_deg: str,
        lat_min: str,
        lat_sec: str,
        lat_hemis: str,
        lat_decimal: str,
        lon_deg: str,
        lon_min: str,
        lon_sec: str,
        lon_hemis: str,
        lon_decimal: str,
        nav_id: str,
        navaid_bearing: str,
        navaid_dist: str,
    ) -> None:
        super().__init__(
            "mil_training_route_points",
            eff_date,
            route_type_code,
            route_id,
            artcc,
        )
        self.route_pt_seq = to_nullable_int(route_pt_seq)
        self.route_pt_id = to_nullable_string(route_pt_id)
        self.next_route_pt_id = to_nullable_string(next_route_pt_id)
        self.segment_text = to_nullable_string(segment_text)
        self.lat_deg = to_nullable_int(lat_deg)
        self.lat_min = to_nullable_int(lat_min)
        self.lat_sec = to_nullable_float(lat_sec)
        self.lat_hemis = HemisCode.from_value(to_nullable_string(lat_hemis))
        self.lat_decimal = to_nullable_float(lat_decimal)
        self.lon_deg = to_nullable_int(lon_deg)
        self.lon_min = to_nullable_int(lon_min)
        self.lon_sec = to_nullable_float(lon_sec)
        self.lon_hemis = HemisCode.from_value(to_nullable_string(lon_hemis))
        self.lon_decimal = to_nullable_float(lon_decimal)
        self.nav_id = to_nullable_string(nav_id)
        self.navaid_bearing = to_nullable_float(navaid_bearing)
        self.navaid_dist = to_nullable_float(navaid_dist)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"ROUTE_PT_SEQ={self.route_pt_seq!r}, "
            f"ROUTE_PT_ID={self.route_pt_id!r}, "
            f"NEXT_ROUTE_PT_ID={self.next_route_pt_id!r}, "
            f"SEGMENT_TEXT={self.segment_text!r}, "
            f"LAT_DEG={self.lat_deg!r}, "
            f"LAT_MIN={self.lat_min!r}, "
            f"LAT_SEC={self.lat_sec!r}, "
            f"LAT_HEMIS={self.lat_hemis!r}, "
            f"LAT_DECIMAL={self.lat_decimal!r}, "
            f"LON_DEG={self.lon_deg!r}, "
            f"LON_MIN={self.lon_min!r}, "
            f"LON_SEC={self.lon_sec!r}, "
            f"LON_HEMIS={self.lon_hemis!r}, "
            f"LON_DECIMAL={self.lon_decimal!r}, "
            f"NAV_ID={self.nav_id!r}, "
            f"NAVAID_BEARING={self.navaid_bearing!r}, "
            f"NAVAID_DIST={self.navaid_dist!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "route_pt_seq",
                "route_pt_id",
                "next_route_pt_id",
                "segment_text",
                "lat_deg",
                "lat_min",
                "lat_sec",
                "lat_hemis",
                "lat_decimal",
                "lon_deg",
                "lon_min",
                "lon_sec",
                "lon_hemis",
                "lon_decimal",
                "nav_id",
                "navaid_bearing",
                "navaid_dist",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "route_pt_seq": self.route_pt_seq,
            "route_pt_id": self.route_pt_id,
            "next_route_pt_id": self.next_route_pt_id,
            "segment_text": self.segment_text,
            "lat_deg": self.lat_deg,
            "lat_min": self.lat_min,
            "lat_sec": self.lat_sec,
            "lat_hemis": self.lat_hemis.value if self.lat_hemis else None,
            "lat_decimal": self.lat_decimal,
            "lon_deg": self.lon_deg,
            "lon_min": self.lon_min,
            "lon_sec": self.lon_sec,
            "lon_hemis": self.lon_hemis.value if self.lon_hemis else None,
            "lon_decimal": self.lon_decimal,
            "nav_id": self.nav_id,
            "navaid_bearing": self.navaid_bearing,
            "navaid_dist": self.navaid_dist,
        }
        return {**base_dict, **this_dict}
