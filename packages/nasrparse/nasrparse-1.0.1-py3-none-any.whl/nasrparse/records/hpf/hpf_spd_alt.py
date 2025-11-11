from nasrparse.functions import to_nullable_string

from ._base import Base


class HPF_SPD_ALT(Base):
    speed_range: str | None
    """Speed Range for Holding Altitude of Record."""
    altitude: str | None
    """Holding Altitude for Speed Range of Record."""

    def __init__(
        self,
        eff_date: str,
        hp_name: str,
        hp_no: str,
        state_code: str,
        country_code: str,
        speed_range: str,
        altitude: str,
    ) -> None:
        super().__init__(
            "holding_speeds_altitudes",
            eff_date,
            hp_name,
            hp_no,
            state_code,
            country_code,
        )
        self.speed_range = to_nullable_string(speed_range)
        self.altitude = to_nullable_string(altitude)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"SPEED_RANGE={self.speed_range!r}, "
            f"ALTITUDE={self.altitude!r}, "
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "speed_range",
                "altitude",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "speed_range": self.speed_range,
            "altitude": self.altitude,
        }
        return {**base_dict, **this_dict}
