"""Irish time index for every DataFrame.

The raw CSVs are exported in UTC. When loaded, the index is converted to
Irish local time (Europe/Dublin) and named ``time_ist``:

    winter: GMT, shown as +00:00      e.g. 2025-01-15 17:00:00+00:00
    summer: IST, shown as +01:00      e.g. 2025-07-15 17:00:00+01:00

Clock changes are handled by the time-zone database:
  * March (clocks forward): local 01:00-01:59 does not exist, so the index
    jumps 00:30 -> 02:00. No data is lost; it is the same continuous series.
  * October (clocks back): local 01:00 and 01:30 occur twice. The two copies
    carry different offsets (+01:00 then +00:00), so the index stays unique
    and correctly ordered. Never strip the time zone (tz_localize(None)),
    or those two half-hours will collide.

Because the index is tz-aware, df.index.hour / .dayofweek / .month give Irish
clock values directly, and joins between DataFrames line up exactly.
"""
import pandas as pd

IRISH_TZ = "Europe/Dublin"
INDEX_NAME = "time_ist"


def to_irish_time(df: pd.DataFrame, tz: str = IRISH_TZ) -> pd.DataFrame:
    """Return a copy with the index converted to Irish local time and named ``time_ist``.

    Naive timestamps are assumed to be UTC. Repeated timestamps are dropped
    (keeping the last) before conversion, so the result has a unique index.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("The DataFrame index must be a DatetimeIndex.")
    df = df.copy()
    idx = df.index.tz_localize("UTC") if df.index.tz is None else df.index
    df.index = idx
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df.index = df.index.tz_convert(tz)
    df.index.name = INDEX_NAME
    return df
