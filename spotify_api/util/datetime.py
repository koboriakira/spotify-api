from datetime import datetime as DatetimeObject
from datetime import date as DateObject
from datetime import timedelta
from typing import Optional


def get_current_day_and_tomorrow(date_str: Optional[str] = None) -> tuple[float, float]:
    """
    指定された日付の0時と翌日の0時のunixtimeを返す。
    指定がない場合は今日の0時と翌日の0時のunixtimeを返す。
    """
    if date_str is None:
        today = DatetimeObject.now()
        return get_current_day_and_tomorrow(date_str=today.strftime("%Y-%m-%d"))

    selected_date = DatetimeObject.strptime(date_str, "%Y-%m-%d")
    unix_today = DatetimeObject(selected_date.year, selected_date.month,
                                selected_date.day).timestamp()
    unix_tomorrow = unix_today + 86400
    return unix_today, unix_tomorrow
