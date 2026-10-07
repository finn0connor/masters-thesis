# masters-thesis

**Sensitivity Analysis of Rare Events in Engineering Systems**
MAI Thesis — Mechanical & Manufacturing Engineering, Trinity College Dublin
Author: Finn O'Connor

## Overview

This project develops a forecasting model for the **Net Imbalance Volume (NIV)** and **imbalance price** in the Irish Single Electricity Market (I-SEM) balancing market, and uses global sensitivity analysis and rare-event methods to understand what drives extreme outcomes.

The system is modelled as a causal chain:

```
Input uncertainty            Engineering system        Market mechanism        Economic outcome
(wind, demand,        ──►    Net Imbalance       ──►   Balancing bid-     ──►  Imbalance
 interconnectors,            Volume (NIV)              offer stack             price
 outages)
```

NIV is treated as the primary engineering variable and the imbalance price as its economic consequence. The focus is on the **tails** of both distributions — rare, high-impact events — rather than average behaviour.

### Methods

| Area | Methods | Main libraries |
|---|---|---|
| Forecasting / surrogates | Gradient-boosted trees, quantile regression, probabilistic forecasting | LightGBM, XGBoost, scikit-learn, statsmodels |
| Input uncertainty | Marginal distributions, vine copulas for dependence | OpenTURNS, pyvinecopulib, SciPy |
| Sensitivity analysis | Morris screening, Sobol variance-based indices | SALib, OpenTURNS |
| Extreme values | Peaks-over-threshold (GPD), block maxima (GEV), return levels | pyextremes, SciPy |
| Rare-event estimation | Importance sampling, subset simulation | OpenTURNS, NumPy |
| Evaluation | Pinball loss, CRPS, interval coverage, tail metrics, rolling-origin backtests | NumPy, pandas |

## Repository structure

```
masters-thesis/
├── README.md                  Project overview and file guide (this file)
├── pyproject.toml             Package metadata and dependencies (managed with uv)
├── uv.lock                    Locked dependency versions for reproducibility
├── .python-version            Python version used (3.12)
├── .gitignore                 Excludes data, credentials, virtual env and caches
├── .gitattributes             Strips notebook outputs on commit (nbstripout)
├── references.bib             Bibliography (BibTeX) for the thesis
│
├── src/imbalance_sa/          Main Python package
│   ├── __init__.py            Package entry point
│   ├── data/                  Data loading, cleaning, time alignment, feature engineering
│   ├── uncertainty/           Input distributions and dependence models (copulas)
│   ├── surrogates/            Forecasting / surrogate models for NIV and imbalance price
│   ├── sensitivity/           Morris screening and Sobol sensitivity analysis
│   ├── rare_events/           Extreme value analysis, importance sampling, subset simulation
│   └── evaluation/            Forecast scoring, backtesting and tail-risk metrics
│
├── notebooks/                 Numbered exploratory notebooks (NN_description.ipynb)
│   └── 01_initial_brainstorming.ipynb   Problem framing and project structure
│
├── notes/                     Research notes and planning (Markdown)
│   ├── 01_brainstorming.md    Initial ideas and scope
│   ├── literature/            One note per paper, named by its citation key
│   ├── concepts/              Methods and theory explained (e.g. Sobol indices, GPD)
│   ├── datasets/              Documentation of each data source and its fields
│   ├── experiments/           Log of each modelling experiment and its results
│   ├── ideas/                 Research ideas and whether they were pursued
│   ├── drafts/                Chapter outlines and draft text
│   ├── meetings/              Supervisor meeting notes
│   ├── weekly/                Weekly progress reviews
│   └── attachments/           Images embedded in notes
│
├── config/                    YAML configuration files for experiments
├── data/                      Local data only — not version-controlled
│   ├── raw/                   Data as extracted from source systems
│   └── processed/             Cleaned, aligned datasets ready for modelling
├── figures/                   Figures generated for the thesis
└── tests/                     Unit tests (pytest)
```

## Data

The analysis uses system-wide Irish market data: imbalance prices, NIV, wind and demand forecasts and outturns, interconnector flows and balancing-market data. No client or confidential commercial data is used.

Data files are **not** stored in this repository. They are kept locally in `data/`, which is excluded by `.gitignore`. Database credentials, where needed, are read from a local `.env` file (also excluded).

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12.

```bash
uv sync                 # create the virtual environment and install dependencies
uv run pytest           # run the test suite
uv run ruff check       # lint
```

To use the environment in Jupyter, select the `.venv` interpreter as the notebook kernel.

## Conventions

- Reusable code lives in `src/imbalance_sa/`; notebooks import from it rather than defining core logic.
- Timestamps are stored in UTC; imbalance settlement periods are 30 minutes.
- Models are validated with time-ordered (rolling-origin) backtests — never random splits — and features use only information available at forecast time.
- Notebook outputs are stripped automatically before commit.
