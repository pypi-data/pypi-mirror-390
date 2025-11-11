from nasrparse.functions import to_nullable_string
from nasrparse.records.types import MTRAgencyTypeCode

from ._base import Base


class MTR_AGY(Base):
    agency_type: MTRAgencyTypeCode
    """MTR Agency Type Code."""
    agency_name: str | None
    """Agency Organization Name"""
    station: str | None
    """Agency Station"""
    address: str | None
    """Agency Address"""
    city: str | None
    """Agency City"""
    state_code: str | None
    """Agency State Post Office Code standard two letter abbreviation for US States and Territories."""
    zip_code: str | None
    """Agency ZIP Code"""
    commercial_no: str | None
    """Agency Commercial Phone Number"""
    dsn_no: str | None
    """Agency DSN Phone Number"""
    hours: str | None
    """Agency Hours"""

    def __init__(
        self,
        eff_date: str,
        route_type_code: str,
        route_id: str,
        artcc: str,
        agency_type: str,
        agency_name: str,
        station: str,
        address: str,
        city: str,
        state_code: str,
        zip_code: str,
        commercial_no: str,
        dsn_no: str,
        hours: str,
    ) -> None:
        super().__init__(
            "mil_training_route_agencies",
            eff_date,
            route_type_code,
            route_id,
            artcc,
        )
        self.agency_type = MTRAgencyTypeCode.from_value(to_nullable_string(agency_type))
        self.agency_name = to_nullable_string(agency_name)
        self.station = to_nullable_string(station)
        self.address = to_nullable_string(address)
        self.city = to_nullable_string(city)
        self.state_code = to_nullable_string(state_code)
        self.zip_code = to_nullable_string(zip_code)
        self.commercial_no = to_nullable_string(commercial_no)
        self.dsn_no = to_nullable_string(dsn_no)
        self.hours = to_nullable_string(hours)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"AGENCY_TYPE={self.agency_type!r}, "
            f"AGENCY_NAME={self.agency_name!r}, "
            f"STATION={self.station!r}, "
            f"ADDRESS={self.address!r}, "
            f"CITY={self.city!r}, "
            f"STATE_CODE={self.state_code!r}, "
            f"ZIP_CODE={self.zip_code!r}, "
            f"COMMERCIAL_NO={self.commercial_no!r}, "
            f"DSN_NO={self.dsn_no!r}, "
            f"HOURS={self.hours!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "agency_type",
                "agency_name",
                "station",
                "address",
                "city",
                "state_code",
                "zip_code",
                "commercial_no",
                "dsn_no",
                "hours",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "agency_type": self.agency_type.value if self.agency_type else None,
            "agency_name": self.agency_name,
            "station": self.station,
            "address": self.address,
            "city": self.city,
            "state_code": self.state_code,
            "zip_code": self.zip_code,
            "commercial_no": self.commercial_no,
            "dsn_no": self.dsn_no,
            "hours": self.hours,
        }
        return {**base_dict, **this_dict}
