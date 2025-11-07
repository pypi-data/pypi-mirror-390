from nasrparse.functions import to_nullable_string

from ._base import Base


class MTR_TERR(Base):
    terrain_seq_no: str | None
    """TERRAIN Text Computer assigned Sequence Number"""
    terrain_text: str | None
    """Terrain Following Operations Text"""

    def __init__(
        self,
        eff_date: str,
        route_type_code: str,
        route_id: str,
        artcc: str,
        terrain_seq_no: str,
        terrain_text: str,
    ) -> None:
        super().__init__(
            "mil_training_route_terrains",
            eff_date,
            route_type_code,
            route_id,
            artcc,
        )
        self.terrain_seq_no = to_nullable_string(terrain_seq_no)
        self.terrain_text = to_nullable_string(terrain_text)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"TERRAIN_SEQ_NO={self.terrain_seq_no!r}, "
            f"TERRAIN_TEXT={self.terrain_text!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "terrain_seq_no",
                "terrain_text",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "terrain_seq_no": self.terrain_seq_no,
            "terrain_text": self.terrain_text,
        }
        return {**base_dict, **this_dict}
