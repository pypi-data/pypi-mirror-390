from nasrparse.functions import to_nullable_string

from ._base import Base


class PFR_BASE(Base):
    origin_city: str | None
    """Origin Facility Associated City Name."""
    origin_state_code: str | None
    """This is the two letter state ID of the Origin Facility location. NULL if outside the US."""
    origin_country_code: str | None
    """Country Code of the Origin Facility Located."""
    dstn_city: str | None
    """Destination Facility Associated City Name."""
    dstn_state_code: str | None
    """This is the two letter state ID of the Destination Facility location. NULL if outside the US."""
    dstn_country_code: str | None
    """Country Code of the Destination Facility Located."""
    special_area_descrip: str | None
    """Preferred Route Area Description."""
    alt_descrip: str | None
    """Preferred Route Altitude Description."""
    aircraft: str | None
    """Aircraft Allowed/Limitations Description"""
    hours: str | None
    """Effective Hours (GMT) Description * All Preferred IFR Routes are in Effect Continuously Unless Otherwise Noted."""
    route_dir_descrip: str | None
    """Route Direction Limitations Description"""
    designator: str | None
    """Preferred Route Designator if applicable"""
    nar_type: str | None
    """North American Route Type (COMMON, NON-COMMON)"""
    inland_fac_fix: str | None
    """North American Route Inland NAV Facility or Fix is the Origin on COMMON EASTBOUND and NON-COMMON (Eastbound or Westbound) and the Destination on COMMON WESTBOUND."""
    coastal_fix: str | None
    """North American Route Coastal Fix is the Origin on COMMON WESTBOUND and the Destination on COMMON EASTBOUND."""
    destination: str | None
    """North American Route Destination for NON_COMMON (Eastbound or Westbound)."""
    route_string: str | None
    """Preferred Route String. *Canadian DPs and STARs will use the generic format of “-DP” and “-STAR”. See the Canadian Aeronautical Data for the correct amendment number for filing."""

    def __init__(
        self,
        eff_date: str,
        origin_id: str,
        dstn_id: str,
        pfr_type_code: str,
        route_no: str,
        origin_city: str,
        origin_state_code: str,
        origin_country_code: str,
        dstn_city: str,
        dstn_state_code: str,
        dstn_country_code: str,
        special_area_descrip: str,
        alt_descrip: str,
        aircraft: str,
        hours: str,
        route_dir_descrip: str,
        designator: str,
        nar_type: str,
        inland_fac_fix: str,
        coastal_fix: str,
        destination: str,
        route_string: str,
    ) -> None:
        super().__init__(
            "preferred_routes",
            eff_date,
            origin_id,
            dstn_id,
            pfr_type_code,
            route_no,
        )
        self.origin_city = to_nullable_string(origin_city)
        self.origin_state_code = to_nullable_string(origin_state_code)
        self.origin_country_code = to_nullable_string(origin_country_code)
        self.dstn_city = to_nullable_string(dstn_city)
        self.dstn_state_code = to_nullable_string(dstn_state_code)
        self.dstn_country_code = to_nullable_string(dstn_country_code)
        self.special_area_descrip = to_nullable_string(special_area_descrip)
        self.alt_descrip = to_nullable_string(alt_descrip)
        self.aircraft = to_nullable_string(aircraft)
        self.hours = to_nullable_string(hours)
        self.route_dir_descrip = to_nullable_string(route_dir_descrip)
        self.designator = to_nullable_string(designator)
        self.nar_type = to_nullable_string(nar_type)
        self.inland_fac_fix = to_nullable_string(inland_fac_fix)
        self.coastal_fix = to_nullable_string(coastal_fix)
        self.destination = to_nullable_string(destination)
        self.route_string = to_nullable_string(route_string)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"ORIGIN_CITY={self.origin_city!r}, "
            f"ORIGIN_STATE_CODE={self.origin_state_code!r}, "
            f"ORIGIN_COUNTRY_CODE={self.origin_country_code!r}, "
            f"DSTN_CITY={self.dstn_city!r}, "
            f"DSTN_STATE_CODE={self.dstn_state_code!r}, "
            f"DSTN_COUNTRY_CODE={self.dstn_country_code!r}, "
            f"SPECIAL_AREA_DESCRIP={self.special_area_descrip!r}, "
            f"ALT_DESCRIP={self.alt_descrip!r}, "
            f"AIRCRAFT={self.aircraft!r}, "
            f"HOURS={self.hours!r}, "
            f"ROUTE_DIR_DESCRIP={self.route_dir_descrip!r}, "
            f"DESIGNATOR={self.designator!r}, "
            f"NAR_TYPE={self.nar_type!r}, "
            f"INLAND_FAC_FIX={self.inland_fac_fix!r}, "
            f"COASTAL_FIX={self.coastal_fix!r}, "
            f"DESTINATION={self.destination!r}, "
            f"ROUTE_STRING={self.route_string!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "origin_city",
                "origin_state_code",
                "origin_country_code",
                "dstn_city",
                "dstn_state_code",
                "dstn_country_code",
                "special_area_descrip",
                "alt_descrip",
                "aircraft",
                "hours",
                "route_dir_descrip",
                "designator",
                "nar_type",
                "inland_fac_fix",
                "coastal_fix",
                "destination",
                "route_string",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "origin_city": self.origin_city,
            "origin_state_code": self.origin_state_code,
            "origin_country_code": self.origin_country_code,
            "dstn_city": self.dstn_city,
            "dstn_state_code": self.dstn_state_code,
            "dstn_country_code": self.dstn_country_code,
            "special_area_descrip": self.special_area_descrip,
            "alt_descrip": self.alt_descrip,
            "aircraft": self.aircraft,
            "hours": self.hours,
            "route_dir_descrip": self.route_dir_descrip,
            "designator": self.designator,
            "nar_type": self.nar_type,
            "inland_fac_fix": self.inland_fac_fix,
            "coastal_fix": self.coastal_fix,
            "destination": self.destination,
            "route_string": self.route_string,
        }
        return {**base_dict, **this_dict}
