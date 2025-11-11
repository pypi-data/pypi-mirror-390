from nasrparse.functions import to_nullable_int, to_nullable_position

from ._base import Base


class MAA_SHP(Base):
    point_seq: int | None
    """Unique Sequence number for MAA Polygon Coordinates."""
    latitude: float | None
    """MAA Polygon Coordinate Latitude (Formatted)"""
    longitude: float | None
    """MAA Polygon Coordinate Longitude (Formatted)"""

    def __init__(
        self,
        eff_date: str,
        maa_id: str,
        point_seq: str,
        latitude: str,
        longitude: str,
    ) -> None:
        super().__init__(
            "misc_activity_shapes",
            eff_date,
            maa_id,
        )
        self.point_seq = to_nullable_int(point_seq)
        self.latitude = to_nullable_position(latitude)
        self.longitude = to_nullable_position(longitude)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"POINT_SEQ={self.point_seq!r}, "
            f"LATITUDE={self.latitude!r}, "
            f"LONGITUDE={self.longitude!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "point_seq",
                "latitude",
                "longitude",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "point_seq": self.point_seq,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }
        return {**base_dict, **this_dict}
