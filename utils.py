
from datetime import datetime
import pytz

def to_local(dt_utc, tz_name):
    tz = pytz.timezone(tz_name)
    return dt_utc.astimezone(tz)

def time_slot_label(local_dt):
    wd = local_dt.weekday()
    hr = local_dt.hour
    if wd == 3:
        return "Thursday Night" if hr >= 18 else "Thursday"
    if wd == 5:
        if hr < 12: return "Saturday Morning"
        if hr < 18: return "Saturday Afternoon"
        return "Saturday Evening"
    if wd == 6:
        if hr < 15: return "Sunday Early"
        if hr < 19: return "Sunday Late"
        return "Sunday Night"
    if wd == 0:
        return "Monday Night" if hr >= 18 else "Monday"
    return local_dt.strftime("%A %I:%M %p")

def implied_prob(ml_price: int) -> float:
    if ml_price < 0:
        return (-ml_price) / ((-ml_price) + 100)
    return 100 / (ml_price + 100)
