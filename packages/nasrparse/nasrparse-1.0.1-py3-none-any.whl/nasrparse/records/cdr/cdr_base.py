from nasrparse.functions import to_nullable_bool, to_nullable_int, to_nullable_string
from nasrparse.records.types import NavigationEquipmentCode

from ._base import Base


class CDR_BASE(Base):
    route_string: str | None
    """The preplanned route of flight associated with a given CDR."""
    dcntr: str | None
    """Departure ARTCC associated with a given CDR."""
    acntr: str | None
    """Arrival ARTCC associated with a given CDR."""
    tcntrs: str | None
    """A list of all Traversed ARTCCs for a given CDR."""
    coordreq: bool | None
    """Y/N indicator as to whether Coordination is required."""
    play: str | None
    """The Playbook Play name for a given CDR."""
    naveqp: NavigationEquipmentCode
    """Navigation Equipment Designator."""
    length: int | None
    """Length of CDR in Nautical Miles"""

    def __init__(
        self,
        rcode: str,
        orig: str,
        dest: str,
        depfix: str,
        route_string: str,
        dcntr: str,
        acntr: str,
        tcntrs: str,
        coordreq: str,
        play: str,
        naveqp: str,
        length: str,
    ) -> None:
        super().__init__(
            "coded_routes",
            rcode,
            orig,
            dest,
            depfix,
        )
        self.route_string = to_nullable_string(route_string)
        self.dcntr = to_nullable_string(dcntr)
        self.acntr = to_nullable_string(acntr)
        self.tcntrs = to_nullable_string(tcntrs)
        self.coordreq = to_nullable_bool(coordreq)
        self.play = to_nullable_string(play)
        self.naveqp = NavigationEquipmentCode.from_value(to_nullable_string(naveqp))
        self.length = to_nullable_int(length)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"ROUTE_STRING={self.route_string!r}, "
            f"DCNTR={self.dcntr!r}, "
            f"ACNTR={self.acntr!r}, "
            f"TCNTRS={self.tcntrs!r}, "
            f"COORDREQ={self.coordreq!r}, "
            f"PLAY={self.play!r}, "
            f"NAVEQP={self.naveqp!r}, "
            f"LENGTH={self.length!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "route_string",
                "dcntr",
                "acntr",
                "tcntrs",
                "coordreq",
                "play",
                "naveqp",
                "length",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "route_string": self.route_string,
            "dcntr": self.dcntr,
            "acntr": self.acntr,
            "tcntrs": self.tcntrs,
            "coordreq": self.coordreq,
            "play": self.play,
            "naveqp": self.naveqp.value if self.naveqp else None,
            "length": self.length,
        }
        return {**base_dict, **this_dict}
