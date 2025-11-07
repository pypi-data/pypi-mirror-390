from nasrparse.functions import to_nullable_string

from ._base import Base


class HPF_CHRT(Base):
    charting_type_desc: str | None
    """Chart on Which Holding Pattern is To Be Depicted."""

    def __init__(
        self,
        eff_date: str,
        hp_name: str,
        hp_no: str,
        state_code: str,
        country_code: str,
        charting_type_desc: str,
    ) -> None:
        super().__init__(
            "holding_charts",
            eff_date,
            hp_name,
            hp_no,
            state_code,
            country_code,
        )
        self.charting_type_desc = to_nullable_string(charting_type_desc)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"CHARTING_TYPE_DESC={self.charting_type_desc!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "charting_type_desc",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "charting_type_desc": self.charting_type_desc,
        }
        return {**base_dict, **this_dict}
