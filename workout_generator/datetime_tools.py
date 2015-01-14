import datetime
import time


def datetime_to_timestamp_ms(dt):
    if dt is None:
        return None
    return int(time.mktime(dt.timetuple()) * 1000 + (dt.microsecond / 1000))


def timestamp_ms_to_datetime(timestamp_ms):
    if timestamp_ms is None:
        return None
    microsecond = (timestamp_ms % 1000) * 1000
    return datetime.datetime.utcfromtimestamp(timestamp_ms / 1000).replace(microsecond=microsecond)


def date_to_datetime(d):
    return datetime.datetime.fromordinal(d.toordinal())
