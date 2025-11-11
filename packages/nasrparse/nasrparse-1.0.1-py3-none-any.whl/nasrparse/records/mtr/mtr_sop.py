from nasrparse.functions import to_nullable_string

from ._base import Base


class MTR_SOP(Base):
    sop_seq_no: str | None
    """SOP Text Computer assigned Sequence Number"""
    sop_text: str | None
    """Standard Operating Procedure Text"""

    def __init__(
        self,
        eff_date: str,
        route_type_code: str,
        route_id: str,
        artcc: str,
        sop_seq_no: str,
        sop_text: str,
    ) -> None:
        super().__init__(
            "mil_training_route_sops",
            eff_date,
            route_type_code,
            route_id,
            artcc,
        )
        self.sop_seq_no = to_nullable_string(sop_seq_no)
        self.sop_text = to_nullable_string(sop_text)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"SOP_SEQ_NO={self.sop_seq_no!r}, "
            f"SOP_TEXT={self.sop_text!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "sop_seq_no",
                "sop_text",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "sop_seq_no": self.sop_seq_no,
            "sop_text": self.sop_text,
        }
        return {**base_dict, **this_dict}
