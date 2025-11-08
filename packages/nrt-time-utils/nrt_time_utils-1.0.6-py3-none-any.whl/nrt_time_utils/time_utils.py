import re

import time
from datetime import datetime

import pytz

from nrt_time_utils.timezone import TIMEZONES_DICT

YMD_HMSF_DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
YMD_HMSF_Z_DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f %Z'
YMD_HMS_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
YMD_HMS_Z_DATE_FORMAT = '%Y-%m-%d %H:%M:%S %Z'
YMD_T_HMS_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
YMD_T_HMS_Z_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S %Z'
YMD_DATE_FORMAT = '%Y-%m-%d'
YMD_Z_DATE_FORMAT = '%Y-%m-%d %Z'
YM_DATE_FORMAT = '%Y-%m'
Y_DATE_FORMAT = '%Y'

MINUTE_SECONDS = 60
HOUR_SECONDS = 60 * MINUTE_SECONDS

SECOND_MS = 1000
MINUTE_MS = 60 * SECOND_MS
HOUR_MS = 60 * MINUTE_MS
DAY_MS = 24 * HOUR_MS


class TimeUtil:

    @classmethod
    def date_ms_to_date_str(
            cls, date_ms: int, date_format: str = YMD_HMSF_DATE_FORMAT, tz=None) -> str:

        return cls.date_ms_to_date_time(date_ms, tz).strftime(date_format)

    @classmethod
    def date_str_to_date_ms(
            cls, date_str: str, date_format: str = YMD_HMSF_DATE_FORMAT) -> int:
        return cls.date_time_to_date_ms(cls.date_str_to_date_time(date_str, date_format))

    @classmethod
    def date_ms_to_date_time(cls, date_ms: int, tz=None) -> datetime:
        tz = cls.get_timezone(tz) if isinstance(tz, str) else tz

        return datetime.fromtimestamp(date_ms / 1000, tz) if date_ms is not None else None

    @staticmethod
    def date_str_to_date_time(date_str: str, date_format: str = YMD_HMSF_DATE_FORMAT) -> datetime:

        dt = datetime.strptime(date_str, date_format)

        if '%Z' in date_format:
            tz = TimeUtil.__parse_timezone_from_str(date_str)
            dt = dt.replace(tzinfo=tz)

        return dt

    @staticmethod
    def date_time_to_date_ms(dt: datetime) -> int:
        return int(dt.timestamp()) * 1000

    @staticmethod
    def get_current_date_ms() -> int:
        return int(round(time.time() * 1000))

    @classmethod
    def get_day_end_date_ms(cls, date_ms: int, tz=None) -> int:
        date_time = cls.date_ms_to_date_time(date_ms, tz)
        date_time = date_time.replace(hour=23, minute=59, second=59)
        return cls.date_time_to_date_ms(date_time) + 999

    @classmethod
    def get_day_start_date_ms(cls, date_ms: int, tz=None) -> int:
        date_time = cls.date_ms_to_date_time(date_ms, tz)
        date_time = date_time.replace(hour=0, minute=0, second=0)
        return cls.date_time_to_date_ms(date_time)

    @staticmethod
    def get_timezone(timezone_str: str):
        tz = TIMEZONES_DICT.get(timezone_str)

        if tz:
            timezone_str = tz['name']

        try:
            return pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f'Unknown timezone: {timezone_str}')

    @classmethod
    def get_timezone_offset_hours(cls, timezone_str: str) -> int:
        tz = TIMEZONES_DICT.get(timezone_str)

        if tz:
            return tz['utc_offset']

        for tz_v in TIMEZONES_DICT.values():
            if tz_v['name'] == timezone_str:
                return tz_v['utc_offset']

        time_zone = cls.get_timezone(timezone_str)

        return int(time_zone.utcoffset(datetime.now()).total_seconds() / HOUR_SECONDS)

    @staticmethod
    def is_leap_year(year: int) -> bool:
        return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

    @classmethod
    def is_timeout_ms(cls, start_time_ms: int, timeout_ms: int) -> bool:
        return cls.get_current_date_ms() - start_time_ms > timeout_ms

    @staticmethod
    def is_date_in_format(date_str: str, date_format: str) -> bool:
        try:
            datetime.strptime(date_str, date_format)
        except ValueError:
            return False

        return True

    @classmethod
    def __parse_timezone_from_str(cls, date_str: str):
        tz_pattern = re.compile(r'.*?\b([A-Za-z_]{3,}(?:/[A-Za-z_]{3,})?)\b')
        match = tz_pattern.match(date_str)

        for tz_str in match.groups():
            if tz_str:
                return cls.get_timezone(tz_str)

        raise ValueError(f'Timezone was not found in {date_str}')
