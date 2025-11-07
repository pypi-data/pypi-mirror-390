from nasrparse.functions.record import to_nullable_string

from ._base import Base


class APT_CON(Base):
    title: str | None
    """Title of Contact (MANAGER, OWNER, ASST-MGR, etc.)"""
    name: str | None
    """Facility Contact Name for Title"""
    address1: str | None
    """Title Address1"""
    address2: str | None
    """Title Address2"""
    title_city: str | None
    """Title City"""
    state: str | None
    """Title State"""
    zip_code: str | None
    """Title Zip Code"""
    zip_plus_four: str | None
    """Title Zip Plus Four"""
    phone_no: str | None
    """Title Phone Number"""

    def __init__(
        self,
        eff_date: str,
        site_no: str,
        site_type_code: str,
        state_code: str,
        arpt_id: str,
        city: str,
        country_code: str,
        title: str,
        name: str,
        address1: str,
        address2: str,
        title_city: str,
        state: str,
        zip_code: str,
        zip_plus_four: str,
        phone_no: str,
    ) -> None:
        super().__init__(
            "airport_contact",
            eff_date,
            site_no,
            site_type_code,
            state_code,
            arpt_id,
            city,
            country_code,
        )
        self.title = to_nullable_string(title)
        self.name = to_nullable_string(name)
        self.address1 = to_nullable_string(address1)
        self.address2 = to_nullable_string(address2)
        self.title_city = to_nullable_string(title_city)
        self.state = to_nullable_string(state)
        self.zip_code = to_nullable_string(zip_code)
        self.zip_plus_four = to_nullable_string(zip_plus_four)
        self.phone_no = to_nullable_string(phone_no)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"TITLE={self.title!r}, "
            f"NAME={self.name!r}, "
            f"ADDRESS1={self.address1!r}, "
            f"ADDRESS2={self.address2!r}, "
            f"TITLE_CITY={self.title_city!r}, "
            f"STATE={self.state!r}, "
            f"ZIP_CODE={self.zip_code!r}, "
            f"ZIP_PLUS_FOUR={self.zip_plus_four!r}, "
            f"PHONE_NO={self.phone_no!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "title",
                "name",
                "address1",
                "address2",
                "title_city",
                "state",
                "zip_code",
                "zip_plus_four",
                "phone_no",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "title": self.title,
            "name": self.name,
            "address1": self.address1,
            "address2": self.address2,
            "title_city": self.title_city,
            "state": self.state,
            "zip_code": self.zip_code,
            "zip_plus_four": self.zip_plus_four,
            "phone_no": self.phone_no,
        }
        return {**base_dict, **this_dict}
