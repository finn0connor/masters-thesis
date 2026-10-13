# Sensitivity Analysis of Rare Events in Engineering Systems

**Forecasting extreme imbalance volumes and prices in the Irish electricity system**

MAI Thesis, Mechanical & Manufacturing Engineering, Trinity College Dublin (30 ECTS)
Author: Finn O'Connor · Supervisor: Dr. Rui Teixeira

---

## Overview

The Irish electricity system has to balance supply and demand in real time. Every half-hour the system ends up short or long of energy because demand and wind forecasts are never exact and plant occasionally fails. The system operator corrects the mismatch by instructing units up or down, starting with the cheapest.

- **Net Imbalance Volume (NIV)** is the net energy the operator has to buy or sell in a settlement period to keep the system balanced. Its sign shows whether the system was short or long.
- **Imbalance price (PIMB)** is the price of correcting that imbalance, set by the most expensive action the operator had to take.

Price depends strongly and non-linearly on NIV. Small imbalances are cheap to resolve, but large ones push the operator up a steep cost curve and can cause extreme price spikes. This project builds a probabilistic forecasting model for NIV and the imbalance price in the I-SEM balancing market, and uses global sensitivity analysis and rare-event methods to find out what drives those extreme outcomes.

### Modelling approach

The system is treated as an uncertainty propagation problem with two linked models:

```
 Inputs known in advance            NIV model            Price model
 (wind & demand forecasts,   ──►      g1        ──►         g2         ──►  Imbalance price
  interconnector schedules,       NIV forecast        (NIV + system state)    forecast
  generation margin, outages,
  calendar, recent NIV)
```

NIV is the engineering system; the imbalance price is its economic consequence. The focus is on the **tails** of both distributions, in both directions, rather than average accuracy alone. The main questions are:

1. Which inputs drive NIV and the imbalance price?
2. Which inputs drive **extreme** price events specifically, and do they differ from the drivers of typical behaviour?
3. How much of the forecast uncertainty comes from each stage of the chain?
4. Do these conclusions hold across different model types?

### Methods

| Area | Methods | Main libraries |
|---|---|---|
| Forecasting / surrogates | Gradient-boosted trees, quantile regression, probabilistic forecasting | LightGBM, XGBoost, scikit-learn, statsmodels |
| Input uncertainty | Marginal distributions, vine copulas for input dependence | OpenTURNS, pyvinecopulib, SciPy |
| Sensitivity analysis | Morris screening, Sobol variance-based indices (grouped and individual) | SALib, OpenTURNS |
| Extreme values | Peaks-over-threshold (GPD), block maxima (GEV), return levels | pyextremes, SciPy |
| Rare-event estimation | Importance sampling, subset simulation | OpenTURNS, NumPy |
| Evaluation | Pinball loss, CRPS, interval coverage, tail metrics, rolling-origin backtests | NumPy, pandas |

## Data

The study period is **1 October 2018 to 30 September 2026**, starting from the go-live of the I-SEM market. All data is system-wide market and grid data; no client or commercial data is used.

| File (`data/raw/`) | Contents |
|---|---|
| `niv/isem_niv_and_pimb_actual.csv` | NIV (MW) and imbalance price (€/MWh), 30-min settlement periods |
| `demand/isem_demand_actual.csv` | All-island (I-SEM) demand outturn |
| `demand/ie_demand_actual.csv` | Ireland-only demand outturn |
| `wind/isem_wind_actual.csv` | All-island wind generation outturn |
| `wind/ie_wind_actual.csv` | Ireland-only wind generation outturn |
| `wind/isem_snsp_actual.csv` | System non-synchronous penetration (SNSP, %) |

All timestamps are stored in UTC. Further inputs (wind and demand forecasts, interconnector flows, outages and balancing-market data) will be added as the project develops. Processed, aligned datasets are written to `data/processed/`. Database credentials, where needed, are read from a local `.env` file that is not version-controlled.

## Repository structure

```
masters-thesis/
├── src/imbalance_sa/          Main Python package
│   ├── paths.py               PROJECT_ROOT, so code runs unchanged on any machine
│   ├── data/                  Data loading, cleaning, time alignment, feature engineering
│   ├── uncertainty/           Input distributions and dependence models (copulas)
│   ├── surrogates/            Forecasting / surrogate models for NIV and imbalance price
│   ├── sensitivity/           Morris screening and Sobol sensitivity analysis
│   ├── rare_events/           Extreme value analysis, importance sampling, subset simulation
│   └── evaluation/            Forecast scoring, backtesting and tail-risk metrics
│
├── scripts/                   Numbered, runnable pipeline steps (NN_name.py)
├── notebooks/                 Numbered exploratory notebooks (NN_name.ipynb)
├── notes/                     Research notes (Obsidian vault, plain Markdown)
│   ├── ideas/                 Thesis proposal, candidate input variables
│   ├── literature/            One note per paper, named by citation key
│   ├── concepts/              Methods and theory (e.g. Sobol indices, GPD)
│   ├── datasets/              Documentation of each data source
│   ├── experiments/           Log of modelling experiments and results
│   ├── drafts/                Chapter outlines and draft text
│   ├── meetings/              Supervisor meeting notes
│   ├── weekly/                Weekly progress reviews
│   └── attachments/           Images embedded in notes
│
├── data/raw/                  Data as extracted from source systems
├── data/processed/            Cleaned, aligned datasets ready for modelling
├── config/                    YAML configuration files for experiments
├── figures/                   Figures for the thesis
├── results/                   Model outputs and metrics (regenerated by scripts, not version-controlled)
├── tests/                     Unit tests (pytest)
├── references.bib             Bibliography (BibTeX, keys as authorYEAR)
└── pyproject.toml, uv.lock    Dependencies, managed with uv
```

## Getting started

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12.

```bash
uv sync                                          # create the environment and install dependencies
uv run python scripts/00_check_environment.py    # check the package and key libraries import
uv run pytest                                    # run the tests
uv run ruff check                                # lint
```

To use the environment in Jupyter or VS Code, select the `.venv` interpreter as the notebook kernel.

Load data with paths relative to the project root, so notebooks and scripts work on any machine:

```python
import pandas as pd
from imbalance_sa.paths import PROJECT_ROOT

niv = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "niv" / "isem_niv_and_pimb_actual.csv")
```

## Conventions

- Reusable functions and classes live in `src/imbalance_sa/`. Scripts and notebooks import from the package rather than defining core logic themselves.
- Scripts are numbered in the order they run and are executed from the repository root, e.g. `uv run python scripts/00_check_environment.py`.
- Timestamps are stored in UTC and converted to Europe/Dublin only for display. Imbalance settlement periods are 30 minutes.
- Models are validated with time-ordered, rolling-origin backtests, never random splits, and features use only information available at the time the forecast is issued.
- Notebook outputs are stripped automatically before commit (nbstripout).

## Status

Work in progress. Done so far: project scaffold, raw data for NIV, imbalance price, demand, wind and SNSP, and a first look at NIV and price in `notebooks/01_initial_brainstorming.ipynb`. Next: data cleaning and alignment, exploratory analysis of the NIV and price tails, and the literature review.
