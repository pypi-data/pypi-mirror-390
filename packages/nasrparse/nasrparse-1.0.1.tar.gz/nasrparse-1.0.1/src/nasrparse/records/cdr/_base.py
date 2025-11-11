from nasrparse.functions import to_nullable_string

from nasrparse.records.table_base import TableBase


class Base(TableBase):
    rcode: str | None
    """Each CDR is uniquely identified by an eight-character alphanumeric code. The Route Code is a concatenation of the Origin, Destination and an alphanumeric route identifier."""
    orig: str | None
    """The CDR Point of Origin is a 3 or 4 character departure airport designator."""
    dest: str | None
    """The CDR Point of Destination is a 3 or 4 character arrival airport designator."""
    depfix: str | None
    """The Departure Fix associated with a given CDR."""

    def __init__(
        self,
        table_name: str,
        rcode: str,
        orig: str,
        dest: str,
        depfix: str,
    ) -> None:
        super().__init__(table_name)
        self.rcode = to_nullable_string(rcode)
        self.orig = to_nullable_string(orig)
        self.dest = to_nullable_string(dest)
        self.depfix = to_nullable_string(depfix)

    def __repr__(self) -> str:
        return (
            f"RCode={self.rcode!r}, "
            f"Orig={self.orig!r}, "
            f"Dest={self.dest!r}, "
            f"DepFix={self.depfix!r}, "
        )

    def ordered_fields(self) -> list:
        return [
            "rcode",
            "orig",
            "dest",
            "depfix",
        ]

    def to_dict(self) -> dict:
        return {
            "rcode": self.rcode,
            "orig": self.orig,
            "dest": self.dest,
            "depfix": self.depfix,
        }
