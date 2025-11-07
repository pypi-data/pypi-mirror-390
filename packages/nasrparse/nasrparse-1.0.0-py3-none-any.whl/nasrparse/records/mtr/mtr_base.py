from nasrparse.functions import to_nullable_string

from ._base import Base


class MTR_BASE(Base):
    fss: str | None
    """All Flight Service Station (FSS) Idents Within 150 Nautical Miles of The Route."""
    time_of_use: str | None
    """Times of Use Text Information."""

    def __init__(
        self,
        eff_date: str,
        route_type_code: str,
        route_id: str,
        artcc: str,
        fss: str,
        time_of_use: str,
    ) -> None:
        super().__init__(
            "mil_training_routes",
            eff_date,
            route_type_code,
            route_id,
            artcc,
        )
        self.fss = to_nullable_string(fss)
        self.time_of_use = to_nullable_string(time_of_use)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"FSS={self.fss}, "
            f"TIME_OF_USE={self.time_of_use}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "fss",
                "time_of_use",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "fss": self.fss,
            "time_of_use": self.time_of_use,
        }
        return {**base_dict, **this_dict}
