from datetime import datetime, date

import re


def to_nullable_bool(string: str) -> bool | None:
    string = string.strip()
    if string == "Y":
        return True
    if string == "N":
        return False
    return None


def to_nullable_date(string: str, format: str) -> date | None:
    string = string.strip()
    if string == "":
        return None
    if format == "YYYY/MM":
        string += "/01"
    try:
        date_object = datetime.strptime(string, "%Y/%m/%d")
        return date_object.date()
    except ValueError:
        print(
            f"{__name__}: Could not convert '{string}' to a date in format '{format}'."
        )
        return None
    except TypeError:
        print(f"{__name__}: Input {string} is not a valid string type.")
        return None


def to_nullable_float(string: str) -> float | None:
    string = string.strip()
    if string == "":
        return None
    try:
        result = float(string)
        return result
    except ValueError:
        print(f"{__name__}: Could not convert '{string}' to a float.")
        return None
    except TypeError:
        print(f"{__name__}: Input {string} is not a valid string type.")
        return None


def to_nullable_int(string: str) -> int | None:
    string = string.strip()
    if string == "":
        return None
    try:
        result = int(string)
        return result
    except ValueError:
        print(f"{__name__}: Could not convert '{string}' to an integer.")
        return None
    except TypeError:
        print(f"{__name__}: Input {string} is not a valid string type.")
        return None


def to_nullable_string(string: str) -> str | None:
    string = string.strip()
    if string == "":
        return None
    return string


MIN_IN_DEG = 60
SEC_IN_MIN = 60


def __min_to_deg(min_val: int) -> float:
    return min_val / MIN_IN_DEG


def __sec_to_deg(sec_val: float) -> float:
    return sec_val / SEC_IN_MIN / MIN_IN_DEG


def to_nullable_position(string: str) -> float | None:
    string = string.strip()
    if string == "":
        return None

    pattern = r"(\d{1,3})-(\d{1,2})-([\d.]+)([NSEWnsew])"
    match = re.match(pattern, string)
    if match is None:
        return None

    deg_s = match.group(1)
    deg = to_nullable_int(deg_s)
    min_s = match.group(2)
    min = to_nullable_int(min_s)
    sec_s = match.group(3)
    sec = to_nullable_float(sec_s)
    hem_s = match.group(4)

    if deg is None or min is None or sec is None:
        return None

    result = deg + __min_to_deg(min) + __sec_to_deg(sec)
    if hem_s in ["W", "S"]:
        result = -result
    return result
