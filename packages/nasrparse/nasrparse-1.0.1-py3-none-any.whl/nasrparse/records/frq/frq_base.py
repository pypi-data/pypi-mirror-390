from nasrparse.functions import to_nullable_float, to_nullable_string

from ._base import Base


class FRQ_BASE(Base):
    artcc_or_fss_id: str | None
    """FACILITY TYPE RCAG contain an identified ARTCC ID and FACILITY TYPE RCO/RCO1 contain an identified FSS ID. The ARTCC ID for an RCAG and the FSS ID for an RCO/RCO1 is included for convenience since that is the resource in NASR you must open to view specific RCAG or RCO/RCO1 information."""
    cpdlc: str | None
    """A Controller Pilot Data Link Communications (CPDLC) remark associated with a FACILITY is listed here."""
    tower_hrs: str | None
    """Only listed for ATCT FACILITY TYPEs where the FACILITY equals the SERVICED FACILITY."""
    serviced_facility: str | None
    """The FACILITY ID (or FACILITY NAME if FACILITY TYPE is RCAG) that is serviced by the frequencies listed. This is a NON-NULL field."""
    serviced_fac_name: str | None
    """The FACILITY NAME that is serviced by the frequencies listed."""
    serviced_site_type: str | None
    """Facility Type of SERVICED FACILITY."""
    lat_decimal: float | None
    """Facility Reference Point Latitude in Decimal Format."""
    lon_decimal: float | None
    """Facility Reference Point Longitude in Decimal Format."""
    serviced_city: str | None
    """Serviced Facility Associated City Name."""
    serviced_state: str | None
    """This is the two letter state ID of the SERVICED FACILITY."""
    serviced_country: str | None
    """Country Post Office Code Serviced Facility Located"""
    tower_or_comm_call: str | None
    """Radio call used by pilot to contact ATC or FSS facility."""
    primary_approach_radio_call: str | None
    """Radio call of facility that furnishes primary approach control."""
    freq: str | None
    """Frequency for SERVICED FACILITY use. In the case of a NAVAID with DME/TACAN Channel, the Frequency is displayed with the Channel - FREQ/CHAN."""
    sectorization: str | None
    """Sectorization based on SERVICED FACILITY or airway boundaries, or limitations based on runway usage. For ARTCC and RCAG, Sectorization identifies the Frequency Altitude as Low, High, Low/High or Ultra-High."""
    freq_use: str | None
    """SERVICED FACILITY frequency use description."""
    remark: str | None
    """Remark Text (Free Form Text that further describes a specific Information Item.)"""

    def __init__(
        self,
        eff_date: str,
        facility: str,
        fac_name: str,
        facility_type: str,
        artcc_or_fss_id: str,
        cpdlc: str,
        tower_hrs: str,
        serviced_facility: str,
        serviced_fac_name: str,
        serviced_site_type: str,
        lat_decimal: str,
        lon_decimal: str,
        serviced_city: str,
        serviced_state: str,
        serviced_country: str,
        tower_or_comm_call: str,
        primary_approach_radio_call: str,
        freq: str,
        sectorization: str,
        freq_use: str,
        remark: str,
    ) -> None:
        super().__init__(
            "frequencies",
            eff_date,
            facility,
            fac_name,
            facility_type,
        )
        self.artcc_or_fss_id = to_nullable_string(artcc_or_fss_id)
        self.cpdlc = to_nullable_string(cpdlc)
        self.tower_hrs = to_nullable_string(tower_hrs)
        self.serviced_facility = to_nullable_string(serviced_facility)
        self.serviced_fac_name = to_nullable_string(serviced_fac_name)
        self.serviced_site_type = to_nullable_string(serviced_site_type)
        self.lat_decimal = to_nullable_float(lat_decimal)
        self.lon_decimal = to_nullable_float(lon_decimal)
        self.serviced_city = to_nullable_string(serviced_city)
        self.serviced_state = to_nullable_string(serviced_state)
        self.serviced_country = to_nullable_string(serviced_country)
        self.tower_or_comm_call = to_nullable_string(tower_or_comm_call)
        self.primary_approach_radio_call = to_nullable_string(
            primary_approach_radio_call
        )
        self.freq = to_nullable_string(freq)
        self.sectorization = to_nullable_string(sectorization)
        self.freq_use = to_nullable_string(freq_use)
        self.remark = to_nullable_string(remark)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} ( "
            f"{super().__repr__()}"
            f"ARTCC_OR_FSS_ID={self.artcc_or_fss_id!r}, "
            f"CPDLC={self.cpdlc!r}, "
            f"TOWER_HRS={self.tower_hrs!r}, "
            f"SERVICED_FACILITY={self.serviced_facility!r}, "
            f"SERVICED_FAC_NAME={self.serviced_fac_name!r}, "
            f"SERVICED_SITE_TYPE={self.serviced_site_type!r}, "
            f"LAT_DECIMAL={self.lat_decimal!r}, "
            f"LON_DECIMAL={self.lon_decimal!r}, "
            f"SERVICED_CITY={self.serviced_city!r}, "
            f"SERVICED_STATE={self.serviced_state!r}, "
            f"SERVICED_COUNTRY={self.serviced_country!r}, "
            f"TOWER_OR_COMM_CALL={self.tower_or_comm_call!r}, "
            f"PRIMARY_APPROACH_RADIO_CALL={self.primary_approach_radio_call!r}, "
            f"FREQ={self.freq!r}, "
            f"SECTORIZATION={self.sectorization!r}, "
            f"FREQ_USE={self.freq_use!r}, "
            f"REMARK={self.remark!r}"
            " )"
        )

    def ordered_fields(self) -> list:
        result = []
        result.extend(super().ordered_fields())
        result.extend(
            [
                "artcc_or_fss_id",
                "cpdlc",
                "tower_hrs",
                "serviced_facility",
                "serviced_fac_name",
                "serviced_site_type",
                "lat_decimal",
                "lon_decimal",
                "serviced_city",
                "serviced_state",
                "serviced_country",
                "tower_or_comm_call",
                "primary_approach_radio_call",
                "freq",
                "sectorization",
                "freq_use",
                "remark",
            ]
        )
        return result

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        this_dict = {
            "artcc_or_fss_id": self.artcc_or_fss_id,
            "cpdlc": self.cpdlc,
            "tower_hrs": self.tower_hrs,
            "serviced_facility": self.serviced_facility,
            "serviced_fac_name": self.serviced_fac_name,
            "serviced_site_type": self.serviced_site_type,
            "lat_decimal": self.lat_decimal,
            "lon_decimal": self.lon_decimal,
            "serviced_city": self.serviced_city,
            "serviced_state": self.serviced_state,
            "serviced_country": self.serviced_country,
            "tower_or_comm_call": self.tower_or_comm_call,
            "primary_approach_radio_call": self.primary_approach_radio_call,
            "freq": self.freq,
            "sectorization": self.sectorization,
            "freq_use": self.freq_use,
            "remark": self.remark,
        }
        return {**base_dict, **this_dict}
