from io import TextIOWrapper
from charset_normalizer import from_path


def open_csv(csv_path: str, encoding_override: str | None = None) -> TextIOWrapper:
    detected_encoding = from_path(csv_path).best()
    final_encoding = (
        encoding_override
        if encoding_override
        else (detected_encoding.encoding if detected_encoding else "utf-8")
    )
    return open(csv_path, encoding=final_encoding, newline="")
