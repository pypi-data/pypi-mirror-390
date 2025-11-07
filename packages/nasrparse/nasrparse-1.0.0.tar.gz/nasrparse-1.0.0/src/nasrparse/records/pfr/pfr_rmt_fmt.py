from nasrparse.functions import to_nullable_int, to_nullable_string
from nasrparse.records.types import PrefRouteTypeCode

from nasrparse.records.table_base import TableBase


class PFR_RMT_FMT(TableBase):
    orig: str | None
    """Origin Facility Location Identifier (Depending on NAR Type and Direction, Origin ID Is either Coastal Fix or Inland NAV Facility or Fix)"""
    route_string: str | None
    """Preferred Route String which starts with Orig and ends with Dest. *Canadian DPs and STARs will use the generic format of “-DP” and “-STAR”. See the Canadian Aeronautical Data for the correct amendment number for filing."""
    dest: str | None
    """Destination Facility Location Identifier (Depending on NAR Type and Direction, Destination ID Is either Airport, Coastal Fix or Inland NAV Facility or Fix)"""
    hours1: str | None
    """Effective Hours (GMT) Description * All Preferred IFR Routes are in Effect Continuously Unless Otherwise Noted."""
    type: PrefRouteTypeCode
    """Type Code of Preferred Route Description."""
    area: str | None
    """Preferred Route Area Description."""
    altitude: str | None
    """Preferred Route Altitude Description."""
    aircraft: str | None
    """Aircraft Allowed/Limitations Description"""
    direction: str | None
    """Route Direction Limitations Description"""
    seq: int | None
    """Route Identifier Sequence Number (1-99)"""
    dcntr: str | None
    """Departure ARTCC associated with a given PFR."""
    acntr: str | None
    """Arrival ARTCC associated with a given PFR."""

    def __init__(
        self,
        orig: str,
        route_string: str,
        dest: str,
        hours1: str,
        type: str,
        area: str,
        altitude: str,
        aircraft: str,
        direction: str,
        seq: str,
        dcntr: str,
        acntr: str,
    ) -> None:
        super().__init__(
            "route_management_tool_format",
        )
        self.orig = to_nullable_string(orig)
        self.route_string = to_nullable_string(route_string)
        self.dest = to_nullable_string(dest)
        self.hours1 = to_nullable_string(hours1)
        self.type = PrefRouteTypeCode.from_value(to_nullable_string(type))
        self.area = to_nullable_string(area)
        self.altitude = to_nullable_string(altitude)
        self.aircraft = to_nullable_string(aircraft)
        self.direction = to_nullable_string(direction)
        self.seq = to_nullable_int(seq)
        self.dcntr = to_nullable_string(dcntr)
        self.acntr = to_nullable_string(acntr)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"ORIG={self.orig!r}, "
            f"ROUTE_STRING={self.route_string!r}, "
            f"DEST={self.dest!r}, "
            f"HOURS1={self.hours1!r}, "
            f"TYPE={self.type!r}, "
            f"AREA={self.area!r}, "
            f"ALTITUDE={self.altitude!r}, "
            f"AIRCRAFT={self.aircraft!r}, "
            f"DIRECTION={self.direction!r}, "
            f"SEQ={self.seq!r}, "
            f"DCNTR={self.dcntr!r}, "
            f"ACNTR={self.acntr!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        return [
            "orig",
            "route_string",
            "dest",
            "hours1",
            "type",
            "area",
            "altitude",
            "aircraft",
            "direction",
            "seq",
            "dcntr",
            "acntr",
        ]

    def to_dict(self) -> dict:
        return {
            "orig": self.orig,
            "route_string": self.route_string,
            "dest": self.dest,
            "hours1": self.hours1,
            "type": self.type.value if self.type else None,
            "area": self.area,
            "altitude": self.altitude,
            "aircraft": self.aircraft,
            "direction": self.direction,
            "seq": self.seq,
            "dcntr": self.dcntr,
            "acntr": self.acntr,
        }
