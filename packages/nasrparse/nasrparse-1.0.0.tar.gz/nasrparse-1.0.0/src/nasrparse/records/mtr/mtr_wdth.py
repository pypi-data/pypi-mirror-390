from nasrparse.functions import to_nullable_string

from ._base import Base


class MTR_WDTH(Base):
    width_seq_no: str | None
    """WIDTH Text Computer assigned Sequence Number"""
    width_text: str | None
    """Route Width Description Text"""

    def __init__(
        self,
        eff_date: str,
        route_type_code: str,
        route_id: str,
        artcc: str,
        width_seq_no: str,
        width_text: str,
    ) -> None:
        super().__init__(
            "mil_training_route_widths",
            eff_date,
            route_type_code,
            route_id,
            artcc,
        )
        self.width_seq_no = to_nullable_string(width_seq_no)
        self.width_text = to_nullable_string(width_text)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"WIDTH_SEQ_NO={self.width_seq_no!r}, "
            f"WIDTH_TEXT={self.width_text!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "width_seq_no",
                "width_text",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "width_seq_no": self.width_seq_no,
            "width_text": self.width_text,
        }
        return {**base_dict, **this_dict}
