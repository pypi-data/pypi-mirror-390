from nasrparse.functions import to_nullable_string

from ._base import Base


class DP_APT(Base):
    body_name: str | None
    """The Name of the Body for which the Airport/Runway End are associated. The Body Name is the first and last Fix of the Segment."""
    body_seq: str | None
    """In the rare case that Body Name is not Unique for a given DP, the BODY_SEQ will uniquely identify the Segment."""
    arpt_id: str | None
    """The associated Airport Identifier."""
    rwy_end_id: str | None
    """The Runway End Identifier if applicable."""

    def __init__(
        self,
        eff_date: str,
        dp_computer_code: str,
        dp_name: str,
        artcc: str,
        body_name: str,
        body_seq: str,
        arpt_id: str,
        rwy_end_id: str,
    ) -> None:
        super().__init__(
            "departure_airports",
            eff_date,
            dp_computer_code,
            dp_name,
            artcc,
        )
        self.body_name = to_nullable_string(body_name)
        self.body_seq = to_nullable_string(body_seq)
        self.arpt_id = to_nullable_string(arpt_id)
        self.rwy_end_id = to_nullable_string(rwy_end_id)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"BODY_NAME={self.body_name!r}, "
            f"BODY_SEQ={self.body_seq!r}, "
            f"ARPT_ID={self.arpt_id!r}, "
            f"RWY_END_ID={self.rwy_end_id!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "body_name",
                "body_seq",
                "arpt_id",
                "rwy_end_id",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "body_name": self.body_name,
            "body_seq": self.body_seq,
            "arpt_id": self.arpt_id,
            "rwy_end_id": self.rwy_end_id,
        }
        return {**base_dict, **this_dict}
