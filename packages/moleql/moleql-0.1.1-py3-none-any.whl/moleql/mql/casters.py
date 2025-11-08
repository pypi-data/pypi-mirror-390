import datetime

from bson import ObjectId

LIST_DEFAULT_SEPARATOR: str = ","
EMPTY_STRING: str = ""


# ---------------------------------------------------------
# CAST AS LIST
# ---------------------------------------------------------
def cast_as_list(value: str) -> list[str]:
    output_list: list[str] = value.strip().split(LIST_DEFAULT_SEPARATOR)
    if output_list == [EMPTY_STRING]:
        return []
    return output_list


# ---------------------------------------------------------
# CAST AS OBJECT ID
# ---------------------------------------------------------
def cast_as_object_id(value: str) -> ObjectId:
    return ObjectId(value)


# ---------------------------------------------------------
# CAST AS OBJECT ID TS
# ---------------------------------------------------------
def cast_as_object_id_ts(value: str) -> datetime.datetime:
    return ObjectId(value).generation_time


# ---------------------------------------------------------
# CAST AS OBJECT ID
# ---------------------------------------------------------
def cast_as_timestamp(value: str) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(int(value))


# ---------------------------------------------------------
# CAST AS OBJECT ID
# ---------------------------------------------------------
def cast_as_str(value: any) -> str:
    return str(value)
