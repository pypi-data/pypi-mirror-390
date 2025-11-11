from nasrparse.functions import to_nullable_int, to_nullable_string

from ._base import Base


class PFR_SEG(Base):
    segment_seq: int | None
    """A sequencing number in multiples of five for each SEG_VALUE. Segment Values are in order adapted for each Preferred Route."""
    seg_value: str | None
    """The Segment ID Value for each Element of the Route String from PFR_BASE."""
    seg_type: str | None
    """The Segment Type of the Segment ID Value."""
    state_code: str | None
    """This is the two letter state ID of the Segment Values that are within the US and are Type FIX, FRD, NAVAID or RADIAL. Segment Values outside the US or Types AIRWAY, DP or STAR are NULL."""
    country_code: str | None
    """Country Code for Types FIX, FRD, NAVAID or RADIAL. Segment Value Types AIRWAY, DP or STAR are NULL."""
    icao_region_code: str | None
    """This is the two letter ICAO Region Code for FIX Segment Types only."""
    nav_type: str | None
    """Specific NAVAID Type for Segment Value Types NAVAID, RADIAL or FRD."""
    next_seg: str | None
    """The Segment ID Value of the Element that directly follows the current Segment Value."""

    def __init__(
        self,
        eff_date: str,
        origin_id: str,
        dstn_id: str,
        pfr_type_code: str,
        route_no: str,
        segment_seq: str,
        seg_value: str,
        seg_type: str,
        state_code: str,
        country_code: str,
        icao_region_code: str,
        nav_type: str,
        next_seg: str,
    ) -> None:
        super().__init__(
            "preferred_route_segments",
            eff_date,
            origin_id,
            dstn_id,
            pfr_type_code,
            route_no,
        )
        self.segment_seq = to_nullable_int(segment_seq)
        self.seg_value = to_nullable_string(seg_value)
        self.seg_type = to_nullable_string(seg_type)
        self.state_code = to_nullable_string(state_code)
        self.country_code = to_nullable_string(country_code)
        self.icao_region_code = to_nullable_string(icao_region_code)
        self.nav_type = to_nullable_string(nav_type)
        self.next_seg = to_nullable_string(next_seg)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"SEGMENT_SEQ={self.segment_seq!r}, "
            f"SEG_VALUE={self.seg_value!r}, "
            f"SEG_TYPE={self.seg_type!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"COUNTRY_CODE={self.country_code!r}, "
            f"ICAO_REGION_CODE={self.icao_region_code!r}, "
            f"NAV_TYPE={self.nav_type!r}, "
            f"NEXT_SEG={self.next_seg!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "segment_seq",
                "seg_value",
                "seg_type",
                "state_code",
                "country_code",
                "icao_region_code",
                "nav_type",
                "next_seg",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "segment_seq": self.segment_seq,
            "seg_value": self.seg_value,
            "seg_type": self.seg_type,
            "state_code": self.state_code,
            "country_code": self.country_code,
            "icao_region_code": self.icao_region_code,
            "nav_type": self.nav_type,
            "next_seg": self.next_seg,
        }
        return {**base_dict, **this_dict}
