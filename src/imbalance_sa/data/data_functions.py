import pandas as pd

# Function to convert dataframe timezone from UTC to Europe/Dublin, handling DST transitions
def convert_tz(df: pd.DataFrame, tz_from: str = "UTC", tz_to: str = "Europe/Dublin") -> pd.DataFrame:
    """
    Convert a DataFrame's datetime index from one time zone to another.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with a datetime index (naive or time-zone aware).
    tz_from : str
        Time zone of the index if it is naive (ignored if the index is already
        tz-aware). Default "UTC".
    tz_to : str
        Target time zone. Default "Europe/Dublin".

    Returns
    -------
    pd.DataFrame
        Copy of the DataFrame with the index converted to tz_to.
    """
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        raise ValueError("The DataFrame index must be a datetime type.")

    df = df.copy()

    # Only localise if the index has no time zone yet
    if df.index.tz is None:
        df.index = df.index.tz_localize(
            tz_from,
            ambiguous="infer",           # repeated hour in October: infer order from the data
            nonexistent="shift_forward", # skipped hour in March: move to the next valid time
        )

    df.index = df.index.tz_convert(tz_to)
    return df



# ---------------------------------------------------------------------------
# Cleaning raw time-series exports
# ---------------------------------------------------------------------------
import re
from pathlib import Path

_UNIT_NAMES = {"€": "eur", "eur": "eur", "€/mwh": "eur_mwh", "eur/mwh": "eur_mwh",
               "mw": "mw", "mwh": "mwh", "%": "pct"}

_TIME_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S")


def _snake_case(name: str) -> str:
    """'IE Demand (MW)' -> 'ie_demand_mw', 'PIMB (€)' -> 'pimb_eur'."""
    match = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", str(name).strip())
    base, unit = (match.group(1), match.group(2)) if match else (str(name), None)
    base = re.sub(r"[^0-9a-zA-Z]+", "_", base).strip("_").lower()
    if unit:
        u = unit.strip().lower()
        u = _UNIT_NAMES.get(u, re.sub(r"[^0-9a-z]+", "_", u.replace("€", "eur").replace("%", "pct")).strip("_"))
        base = f"{base}_{u}" if u else base
    return base


def _parse_times(values: pd.Series) -> pd.Series:
    """Parse timestamps, trying ISO (2018-10-01 00:00:00) then day-first (01/10/2018 00:00)."""
    text = values.astype(str).str.strip()
    for fmt in _TIME_FORMATS:
        parsed = pd.to_datetime(text, format=fmt, errors="coerce")
        if parsed.notna().mean() > 0.99:
            return parsed
    return pd.to_datetime(text, dayfirst=True, errors="coerce")


def clean_timeseries(
    data: "pd.DataFrame | str | Path",
    freq: str | None = None,
    agg: str = "mean",
    fill_gaps: bool = True,
    local_columns: bool = True,
    time_col: str | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Clean a raw time-series export (CSV path or DataFrame) into a standard format.

    Steps
    -----
    1. Read the CSV (if a path is given).
    2. Find the time column (first column containing 'time' or 'date', or `time_col`),
       parse it (ISO or day-first formats) and set it as a UTC index named 'time_utc'.
    3. Rename value columns to snake_case with units, e.g. 'PIMB (€)' -> 'pimb_eur'.
    4. Convert values to numbers (anything unparseable becomes NaN).
    5. Remove duplicate timestamps (keeping the last) and sort by time.
    6. Optionally resample to `freq` (e.g. '30min'), aggregating with `agg`.
    7. Optionally insert missing periods as NaN rows so the series is evenly spaced.
    8. Optionally add Irish local-time columns (the index stays in UTC).

    Parameters
    ----------
    data : DataFrame, str or Path
        Raw data, or a path to a CSV file. Timestamps must be in UTC.
    freq : str, optional
        Target resolution, e.g. '30min'. None keeps the original resolution.
    agg : str
        Aggregation used when resampling ('mean', 'sum', 'last', ...).
    fill_gaps : bool
        Insert NaN rows for missing periods (default True).
    local_columns : bool
        Add 'time_local' (Europe/Dublin), 'hour_local', 'dow_local' (0 = Monday),
        'month_local' and 'is_weekend' (default True).
    time_col : str, optional
        Name of the time column if it cannot be detected automatically.
    verbose : bool
        Print a short cleaning report.

    Returns
    -------
    pd.DataFrame
        Clean DataFrame indexed by 'time_utc' (tz-aware UTC). A summary of the
        cleaning is stored in `df.attrs["cleaning_report"]`.
    """
    source = str(data) if isinstance(data, (str, Path)) else "DataFrame"
    df = pd.read_csv(data) if isinstance(data, (str, Path)) else data.copy()

    # --- 1-2. time column -> UTC index ---------------------------------------
    if time_col is None:
        candidates = [c for c in df.columns if re.search(r"time|date", str(c), re.IGNORECASE)]
        time_col = candidates[0] if candidates else df.columns[0]
    times = _parse_times(df[time_col])
    unparsed = int(times.isna().sum())
    df = df.loc[times.notna()].drop(columns=time_col)
    df.index = pd.DatetimeIndex(times[times.notna()]).tz_localize("UTC")
    df.index.name = "time_utc"

    # --- 3-4. column names and numeric values --------------------------------
    df.columns = [_snake_case(c) for c in df.columns]
    df = df.apply(pd.to_numeric, errors="coerce")

    # --- 5. duplicates and ordering ------------------------------------------
    duplicates = int(df.index.duplicated(keep="last").sum())
    df = df[~df.index.duplicated(keep="last")].sort_index()

    # --- 6. resolution -------------------------------------------------------
    original_step = df.index.to_series().diff().median()
    if freq is not None:
        df = df.resample(freq).agg(agg)
    step = pd.Timedelta(freq) if freq is not None else original_step

    # --- 7. missing periods --------------------------------------------------
    full_index = pd.date_range(df.index.min(), df.index.max(), freq=step, tz="UTC", name="time_utc")
    missing = int(len(full_index.difference(df.index)))
    if fill_gaps and missing:
        df = df.reindex(full_index)

    # --- 8. Irish local-time columns -----------------------------------------
    if local_columns:
        local = df.index.tz_convert("Europe/Dublin")
        df.insert(0, "time_local", local)
        df.insert(1, "hour_local", local.hour)
        df.insert(2, "dow_local", local.dayofweek)
        df.insert(3, "month_local", local.month)
        df.insert(4, "is_weekend", local.dayofweek >= 5)

    report = {
        "source": source,
        "rows": len(df),
        "start_utc": df.index.min(),
        "end_utc": df.index.max(),
        "original_resolution": original_step,
        "resolution": step,
        "unparsed_timestamps_dropped": unparsed,
        "duplicate_timestamps_dropped": duplicates,
        "missing_periods": missing,
        "missing_filled_with_nan": bool(fill_gaps and missing),
        "nan_values_per_column": df.drop(
            columns=["time_local", "hour_local", "dow_local", "month_local", "is_weekend"],
            errors="ignore").isna().sum().to_dict(),
    }
    df.attrs["cleaning_report"] = report

    if verbose:
        print(f"Cleaned {source}")
        print(f"  {report['rows']:,} rows, {report['start_utc']} to {report['end_utc']}")
        print(f"  resolution: {report['original_resolution']}"
              + (f" -> {report['resolution']} ({agg})" if freq else ""))
        print(f"  dropped: {unparsed} unparsed timestamps, {duplicates} duplicate timestamps")
        print(f"  missing periods: {missing}" + (" (inserted as NaN)" if fill_gaps and missing else ""))

    return df
