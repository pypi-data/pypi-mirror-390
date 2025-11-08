from datetime import datetime

from h5_info.constants import DATE_FORMAT, DATETIME_FORMAT_S, DATETIME_FORMAT_S_TIME_DASHED


def read_datetime(date_string) -> datetime:
    """Reads the datetime from the given string.
    Tries to read the datetime in various formats until it finds match"""
    try:
        return datetime.strptime(date_string, DATE_FORMAT)
    except ValueError:
        try:
            return datetime.strptime(date_string, DATETIME_FORMAT_S)
        except ValueError:
            return datetime.strptime(date_string, DATETIME_FORMAT_S_TIME_DASHED)
