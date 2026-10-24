"""Check that the environment is set up and the project package can be imported.

Run from the repository root:
    uv run python scripts/00_check_environment.py
"""

from importlib.metadata import version

import masters_thesis

PACKAGES = [
    "numpy",
    "pandas",
    "scipy",
    "scikit-learn",
    "statsmodels",
    "lightgbm",
    "xgboost",
    "SALib",
    "openturns",
    "pyextremes",
    "pyvinecopulib",
]


def main() -> None:
    print(f"masters_thesis imported from: {masters_thesis.__file__}")
    for name in PACKAGES:
        print(f"{name:<15} {version(name)}")


if __name__ == "__main__":
    main()
