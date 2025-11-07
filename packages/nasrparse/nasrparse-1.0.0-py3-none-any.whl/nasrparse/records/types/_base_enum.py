from enum import Enum
from typing import Self


class BaseEnum(Enum):
    def __init_subclass__(cls):
        super().__init_subclass__()
        if not hasattr(cls, "NULL"):
            raise TypeError(f"{cls.__name__} must define a NULL member")

    @classmethod
    def from_value(cls, value: str | None) -> Self:
        if value is None:
            return cls.NULL
        return cls._value2member_map_.get(value, cls.NULL)
