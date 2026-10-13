"""Project root that works on any machine.

Found from this file's location, so code never needs a hard-coded path like
C:\\Users\\<name>\\... and runs unchanged on every laptop.

Usage:
    from imbalance_sa.paths import PROJECT_ROOT
    df = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "wind" / "isem_wind_actual.csv")
"""

from pathlib import Path

# src/imbalance_sa/paths.py -> parents[2] is the repository root (masters-thesis)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
