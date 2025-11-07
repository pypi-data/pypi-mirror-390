from nasrparse.functions import to_nullable_int, to_nullable_string
from nasrparse.records.types import PointCode

from ._base import Base


class STAR_RTE(Base):
    route_portion_type: str | None
    """The Segment is identified as either a Transition or Body."""
    route_name: str | None
    """The Transition or Body Name."""
    body_seq: str | None
    """In the rare case that Body Name is not Unique for a given STAR, the BODY_SEQ will uniquely identify the Segment."""
    transition_computer_code: str | None
    """FAA-Assigned Computer Identifier for the TRANSITION."""
    point_seq: int | None
    """Sequencing number in multiples of ten. Points are in order adapted for given Segment."""
    point: str | None
    """The FIX or NAVAID adapted on the Segment."""
    icao_region_code: str | None
    """This is the two letter ICAO Region Code for FIX Point Types only."""
    point_type: PointCode
    """Specific FIX or NAVAID Type."""
    next_point: str | None
    """The Point that directly follows the current Point on an individual segment."""
    arpt_rwy_assoc: str | None
    """The list of APT and/or APT/RWY associated with a given Segment."""

    def __init__(
        self,
        eff_date: str,
        star_computer_code: str,
        artcc: str,
        route_portion_type: str,
        route_name: str,
        body_seq: str,
        transition_computer_code: str,
        point_seq: str,
        point: str,
        icao_region_code: str,
        point_type: str,
        next_point: str,
        arpt_rwy_assoc: str,
    ) -> None:
        super().__init__(
            "arrival_routes",
            eff_date,
            star_computer_code,
            artcc,
        )
        self.route_portion_type = to_nullable_string(route_portion_type)
        self.route_name = to_nullable_string(route_name)
        self.body_seq = to_nullable_string(body_seq)
        self.transition_computer_code = to_nullable_string(transition_computer_code)
        self.point_seq = to_nullable_int(point_seq)
        self.point = to_nullable_string(point)
        self.icao_region_code = to_nullable_string(icao_region_code)
        self.point_type = PointCode.from_value(to_nullable_string(point_type))
        self.next_point = to_nullable_string(next_point)
        self.arpt_rwy_assoc = to_nullable_string(arpt_rwy_assoc)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"ROUTE_PORTION_TYPE={self.route_portion_type!r}, "
            f"ROUTE_NAME={self.route_name!r}, "
            f"BODY_SEQ={self.body_seq!r}, "
            f"TRANSITION_COMPUTER_CODE={self.transition_computer_code!r}, "
            f"POINT_SEQ={self.point_seq!r}, "
            f"POINT={self.point!r}, "
            f"ICAO_REGION_CODE={self.icao_region_code!r}, "
            f"POINT_TYPE={self.point_type!r}, "
            f"NEXT_POINT={self.next_point!r}, "
            f"ARPT_RWY_ASSOC={self.arpt_rwy_assoc!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "route_portion_type",
                "route_name",
                "body_seq",
                "transition_computer_code",
                "point_seq",
                "point",
                "icao_region_code",
                "point_type",
                "next_point",
                "arpt_rwy_assoc",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "route_portion_type": self.route_portion_type,
            "route_name": self.route_name,
            "body_seq": self.body_seq,
            "transition_computer_code": self.transition_computer_code,
            "point_seq": self.point_seq,
            "point": self.point,
            "icao_region_code": self.icao_region_code,
            "point_type": self.point_type.value if self.point_type else None,
            "next_point": self.next_point,
            "arpt_rwy_assoc": self.arpt_rwy_assoc,
        }
        return {**base_dict, **this_dict}
