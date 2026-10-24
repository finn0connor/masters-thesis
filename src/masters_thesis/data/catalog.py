"""Every CSV in data/ as a named DataFrame, found automatically.

    from masters_thesis.data.catalog import data

    data.ie_niv_actual_mw          # DataFrame, loaded on first use
    data.ie_da_mcv_wind_mw
    data.list()                    # every available name, with its file
    data.list("ida1")              # names containing "ida1"

Drop a new CSV anywhere under data/ and it appears as data.<name> the next time
you call data.refresh() or restart the kernel. Nothing to register by hand.

Names come from the file name: the leading D_ID is dropped and the rest is
lower snake_case, e.g. 13162_IE_DA_MCV_Wind_MW.csv -> ie_da_mcv_wind_mw.
Files starting with "_" (e.g. _gap_report.csv) are skipped.

Each DataFrame is indexed by Irish local time, ``time_ist`` (Europe/Dublin:
GMT in winter, IST in summer; see timezone.py). The CSVs themselves stay in
UTC. The value column
"quantity" is renamed to the dataset name; forecast files keep their
trading_day / auction / cutoff_utc / tick_utc columns.
"""
import re
from pathlib import Path

import pandas as pd

from masters_thesis.data_functions.timezone import to_irish_time
from masters_thesis.paths import PROJECT_ROOT

DATA_DIR = PROJECT_ROOT / "data"
_TIME_COLS = ("time_utc", "cutoff_utc", "tick_utc")


def dataset_name(path: Path) -> str:
    """'13162_IE_DA_MCV_Wind_MW.csv' -> 'ie_da_mcv_wind_mw'."""
    stem = re.sub(r"^\d+_", "", path.stem)
    return re.sub(r"[^0-9a-z]+", "_", stem.lower()).strip("_")


def load_csv(path: str | Path) -> pd.DataFrame:
    """Read one exported CSV into a DataFrame indexed by Irish time (time_ist)."""
    path = Path(path)
    df = pd.read_csv(path)
    if "time_utc" not in df.columns:   # CSVs are exported in UTC
        raise ValueError(f"{path.name} has no 'time_utc' column (columns: {list(df.columns)})")
    for col in _TIME_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True)
    df = df.drop(columns=["dim_id"], errors="ignore")
    df = df.rename(columns={"quantity": dataset_name(path)})
    df = df.set_index("time_utc")
    return to_irish_time(df)    # index -> time_ist (Europe/Dublin), duplicates dropped, sorted


class DataCatalog:
    """Attribute access to every CSV under a folder, loaded lazily and cached."""

    def __init__(self, root: Path = DATA_DIR):
        self._root = Path(root)
        self._files: dict[str, Path] = {}
        self._cache: dict[str, pd.DataFrame] = {}
        self.refresh()

    def refresh(self) -> None:
        """Rescan the folder for new or removed CSVs."""
        files = {}
        for p in sorted(self._root.rglob("*.csv")):
            if p.name.startswith("_"):
                continue
            name = dataset_name(p)
            if name in files:
                raise ValueError(f"Two files map to '{name}': {files[name]} and {p}")
            files[name] = p
        self._files = files
        self._cache = {k: v for k, v in self._cache.items() if k in files}

    def __getattr__(self, name: str) -> pd.DataFrame:
        if name.startswith("_"):
            raise AttributeError(name)
        if name not in self._files:
            raise AttributeError(f"No dataset '{name}'. Use data.list() to see what's available.")
        if name not in self._cache:
            self._cache[name] = load_csv(self._files[name])
        return self._cache[name]

    def __getitem__(self, name: str) -> pd.DataFrame:
        return getattr(self, name)

    def __dir__(self):
        return list(self._files) + ["list", "refresh", "load_all", "path"]

    def path(self, name: str) -> Path:
        return self._files[name]

    def list(self, contains: str = "") -> pd.Series:
        """Available dataset names (filtered by a substring), with their files."""
        rows = {n: str(p.relative_to(self._root)) for n, p in self._files.items() if contains.lower() in n}
        return pd.Series(rows, name="file", dtype="object")

    def load_all(self, contains: str = "") -> dict[str, pd.DataFrame]:
        """Load every dataset (or those matching a substring) and return them as a dict."""
        return {n: getattr(self, n) for n in self._files if contains.lower() in n}


data = DataCatalog()