import re
from datetime import datetime
from typing import Any


def exact_unix_validator(value: Any) -> datetime | None:
    if value is None:
        return None
    elif isinstance(value, str) and re.match(r"\/Date\((\d{13})\)\/", value):
        ts = int(re.sub(r"\/Date\((\d{13})\)\/", r"\1", value))
        return datetime.fromtimestamp(ts / 1000)

    raise ValueError(
        "Input value does not correspond to exact online unix timestamp (string embedded 13-digit millisecond Unix timestamp) format (e.g. '/Date(1758283747417)/')"
    )


def guid_validator(value: Any):
    if value is None:
        return None
    elif isinstance(value, str) and re.match(
        "^(?:\\{{0,1}(?:[0-9a-fA-F]){8}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){12}\\}{0,1})$",
        value,
    ):
        return value
    raise ValueError("Input is not a string or is not a valid GUID.")


def nested_results_validator(value: Any):
    if isinstance(value, dict):
        if "results" in value:
            return value["results"]
    raise ValueError("Input did not contain nested results.")
