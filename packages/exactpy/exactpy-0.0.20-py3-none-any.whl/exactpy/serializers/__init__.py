from datetime import datetime

from pydantic import FieldSerializationInfo


def exact_unix_transformer(
    dt: datetime | None, info: FieldSerializationInfo
) -> str | datetime | None:
    if dt is None:
        return None
    elif isinstance(info.context, dict):
        if info.context.get("output", "") == "spark":
            return dt
    return f"/Date({int(dt.timestamp() * 1000)})/"
