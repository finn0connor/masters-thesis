---
type: idea
created: 2026-10-07
status: draft
tags: [idea, variables, sensitivity-analysis]
---
# Variables Driving the NIV and PIMB

> [!summary] Purpose
> A deliberately broad list of candidate input variables for the NIV model ($g_1$) and the imbalance price (PIMB) model ($g_2$). The aim is not to decide in advance which variables matter but to include every plausible driver, then let sensitivity analysis decide: **Morris screening** removes the variables with negligible influence, and **Sobol indices** quantify the contribution of those that remain, both to average behaviour and to extreme events.

## 1. How the List Feeds the Sensitivity Analysis

1. **Assemble** every candidate variable below for the full data period.
2. **Check availability.** For forecasting, a variable may only be used if it is known before the forecast is made. Variables only known afterwards (marked *ex-post*) are excluded from the forecasting models but can still be used in an explanatory analysis of what caused past imbalances.
3. **Group** variables into the factor groups below. Many variables are strongly correlated (e.g. wind forecast and residual demand), which makes individual Sobol indices unstable. Group-level indices give a clear first answer, e.g. "renewable forecast changes explain X% of NIV variance".
4. **Screen** with Morris to remove non-influential variables within each group.
5. **Quantify** with Sobol indices at group level, then at variable level within the influential groups.
6. **Compare** rankings for average behaviour against rankings for extreme events, and against the expectations recorded in the final column.

Calendar variables (time of day, season, holidays) are deterministic. They are treated as **conditioning variables** (the analysis is repeated for, say, winter peaks versus summer nights) rather than as random inputs.

**Column key.** *Model:* $g_1$ = NIV model, $g_2$ = imbalance price (PIMB) model. *Timing:* **ex-ante** = known before the forecast is made; **lagged** = only previous periods' values may be used; **ex-post** = known only after the event. *Expected:* prior expectation of influence (High / Medium / Low), recorded now so it can be compared with the Sobol results later.

## 2. Candidate Variables

### 2.1 Calendar and time
| Variable | Description | Model | Timing | Expected |
|---|---|---|---|---|
| Time of day | Settlement period (1–48) | $g_1$, $g_2$ | ex-ante | High |
| Day of week | Monday–Sunday | $g_1$, $g_2$ | ex-ante | Medium |
| Working day / weekend / holiday | Irish and NI public holidays | $g_1$, $g_2$ | ex-ante | Medium |
| Time of year | Month or day of year (seasonality) | $g_1$, $g_2$ | ex-ante | Medium |
| Clock-change and holiday-adjacent days | Unusual demand days | $g_1$ | ex-ante | Low |

### 2.2 Renewable generation
| Variable | Description | Model | Timing | Expected |
|---|---|---|---|---|
| System-wide wind generation (actual) | Metered wind output | $g_1$ | ex-post (lagged only) | High |
| Irish wind forecast | Latest forecast before the forecast time | $g_1$, $g_2$ | ex-ante | High |
| Wind forecast uncertainty | Spread between high and low wind scenarios | $g_1$ | ex-ante | High |
| Wind forecast change since day-ahead | Latest forecast minus forecast at the day-ahead auction | $g_1$ | ex-ante | **Very high** |
| Wind forecast change since each intraday auction | Change since IDA1, IDA2, IDA3 | $g_1$ | ex-ante | **Very high** |
| Wind forecast error, recent periods | Actual minus forecast in previous periods | $g_1$ | lagged | High |
| Wind ramp rate | Forecast change in wind output over the next hours | $g_1$ | ex-ante | Medium |
| Wind cleared vs forecast | Wind volume sold at day-ahead compared with its forecast | $g_1$ | ex-ante | High |
| Wind dispatch-down / curtailment | Wind reduced by the system operator | $g_1$, $g_2$ | lagged | Medium |
| System-wide solar generation (actual) | Metered solar output | $g_1$ | ex-post (lagged only) | Low–Medium |
| Irish solar forecast | Latest forecast | $g_1$ | ex-ante | Low–Medium |
| Solar forecast change since day-ahead | As for wind | $g_1$ | ex-ante | Medium (rising) |
| GB wind and solar forecasts | British renewable output | $g_2$ | ex-ante | Medium |
| GB wind and solar forecast changes | Change since day-ahead | $g_2$ | ex-ante | Low–Medium |
| Installed wind and solar capacity | Structural trend over the eight years | $g_1$, $g_2$ | ex-ante | Medium |

### 2.3 Demand
| Variable | Description | Model | Timing | Expected |
|---|---|---|---|---|
| System-wide demand (actual) | Metered demand, Ireland and NI | $g_1$ | ex-post (lagged only) | Medium |
| Demand forecast | Latest system operator forecast | $g_1$, $g_2$ | ex-ante | Medium |
| Demand forecast change since day-ahead | Latest minus day-ahead forecast | $g_1$ | ex-ante | High |
| Demand forecast error, recent periods | Actual minus forecast | $g_1$ | lagged | High |
| Residual demand | Demand minus wind and solar | $g_1$, $g_2$ | ex-ante | High |
| Residual demand change since day-ahead | Combined renewable and demand forecast change | $g_1$ | ex-ante | **Very high** |
| Temperature | Drives heating demand and demand forecast error | $g_1$ | ex-ante | Low–Medium |

### 2.4 Thermal and conventional plant
| Variable | Description | Model | Timing | Expected |
|---|---|---|---|---|
| Available thermal capacity | Gas, coal, oil, biomass capacity available | $g_2$ | ex-ante | High |
| Thermal capacity on outage (MW) | Planned and forced outages | $g_1$, $g_2$ | ex-ante | Medium |
| Number of plants on outage | Count, with NI must-run units separately | $g_2$ | ex-ante | Medium |
| Unplanned trips | Units tripping close to real time | $g_1$ | lagged | High (for extremes) |
| Capacity margin | Available capacity minus residual demand | $g_2$ | ex-ante | **Very high** (for extremes) |
| Largest unit online | Sets reserve requirement | $g_2$ | ex-ante | Low–Medium |
| Must-run / minimum generation constraints | Units that must run for system stability | $g_1$, $g_2$ | ex-ante | Medium |

### 2.5 Flexibility and storage
| Variable | Description | Model | Timing | Expected |
|---|---|---|---|---|
| Available flexible capacity | Demand response, hydro, pumped storage | $g_2$ | ex-ante | Medium |
| Turlough Hill increase / decrease bid prices | Cost of the main flexible unit, proxy for balancing cost | $g_2$ | ex-ante | High |
| Battery capacity available | Installed and available battery storage | $g_1$, $g_2$ | ex-ante | High (post-2021) |
| Battery state of charge | Aggregate stored energy, if available | $g_2$ | ex-ante / lagged | Medium |

### 2.6 Interconnection
| Variable | Description | Model | Timing | Expected |
|---|---|---|---|---|
| Available interconnector capacity | Total, and per interconnector (Moyle, EWIC, Greenlink) | $g_1$, $g_2$ | ex-ante | High |
| Scheduled interconnector flows | Day-ahead and after each intraday auction | $g_1$, $g_2$ | ex-ante | High |
| Change in interconnector schedule since day-ahead | Flow changes from intraday trading | $g_1$ | ex-ante | Medium |
| Greenlink in service | Indicator from 29 January 2025 | $g_1$, $g_2$ | ex-ante | Medium |
| GB system price | British imbalance price | $g_2$ | lagged | Medium |
| GB system imbalance direction | Whether GB is short or long | $g_2$ | lagged | Medium |

### 2.7 Market positions
| Variable | Description | Model | Timing | Expected |
|---|---|---|---|---|
| Day-ahead cleared volumes by unit type | Suppliers, thermal, flexible, renewable, other | $g_1$ | ex-ante | Medium |
| Intraday traded volumes | Volume traded in IDA1/2/3 | $g_1$ | ex-ante | Medium |
| Net position change from day-ahead to final intraday | How much the market re-traded | $g_1$ | ex-ante | Medium |

### 2.8 Prices and fuel
| Variable | Description | Model | Timing | Expected |
|---|---|---|---|---|
| Irish day-ahead price | DAM clearing price | $g_2$ | ex-ante | **Very high** (sets price level) |
| Irish intraday auction prices | IDA1, IDA2, IDA3 | $g_2$ | ex-ante | High |
| Day-ahead to intraday price spread | Indicates the direction the market expects | $g_1$, $g_2$ | ex-ante | Medium |
| Irish day-ahead price forecast | Central, low and high | $g_2$ | ex-ante | Low (once actual DA price is known) |
| GB day-ahead price | Including N2EX vs EPEX spread | $g_2$ | ex-ante | Medium |
| GB half-hourly and intraday prices | HH price, GB IDA1/2 | $g_2$ | ex-ante | Medium |
| GB price forecast error | From previous days only | $g_2$ | lagged | Low |
| French day-ahead price | Continental price signal | $g_2$ | ex-ante | Low |
| GB gas price | Main driver of thermal marginal cost | $g_2$ | ex-ante | High |
| Carbon price | EU ETS / UK ETS | $g_2$ | ex-ante | Low–Medium |

### 2.9 Recent balancing outcomes
| Variable | Description | Model | Timing | Expected |
|---|---|---|---|---|
| NIV, recent periods | NIV in the last 1–6 periods | $g_1$ | lagged | **Very high** (persistence) |
| Irish imbalance price (PIMB), recent periods | Last published half-hourly and 5-minute prices | $g_1$, $g_2$ | lagged | High |
| BOA stack: recent accepted actions | Volume and price of recently accepted bids and offers | $g_2$ | lagged | High |
| BOA stack: shape | Offered volume within set price bands, slope of the stack | $g_2$ | ex-ante / lagged | **Very high** (for extremes) |
| System actions | Volume of actions taken for non-energy reasons (constraints, reserve) | $g_2$ | lagged | Medium |

### 2.10 Weather and structural indicators
| Variable | Description | Model | Timing | Expected |
|---|---|---|---|---|
| Storm / high-wind cut-out risk | Wind speeds near turbine cut-out (large sudden wind losses) | $g_1$ | ex-ante | High (for extremes) |
| Fog / low-irradiance events | Solar forecast risk | $g_1$ | ex-ante | Low |
| Gas crisis period | Indicator or gas price level, 2021–22 | $g_2$ | ex-ante | Medium |
| Market rule changes | Indicators for changes in balancing or pricing rules | $g_1$, $g_2$ | ex-ante | To confirm |

## 3. Variable Groups for Sobol Analysis

| Group | Variables (sections) | Main model |
|---|---|---|
| Calendar | 2.1 | Conditioning |
| Renewable forecasts and changes | 2.2 | $g_1$ |
| Demand | 2.3 | $g_1$ |
| Thermal availability and margin | 2.4 | $g_2$ |
| Flexibility and storage | 2.5 | $g_2$ |
| Interconnection | 2.6 | $g_1$, $g_2$ |
| Market positions | 2.7 | $g_1$ |
| Price and fuel levels | 2.8 | $g_2$ |
| Recent balancing outcomes | 2.9 | $g_1$, $g_2$ |
| Weather and structural | 2.10 | $g_1$, $g_2$ |

> [!remark] Hypotheses to test
> - **NIV** is driven mainly by changes in wind and residual demand forecasts after the market has traded, and by persistence from recent periods.
> - **Average price** is driven mainly by price and fuel levels (day-ahead price, gas).
> - **Extreme prices** are driven by a different set: low capacity margin, a steep balancing stack, large NIV, and limited interconnector or storage headroom.
>
> The sensitivity analysis will test whether the drivers of average and extreme behaviour really differ in this way.

## 4. To Check
- [ ] Publication time of each variable, especially NIV, PIMB and the BOA data, to confirm which can be used ex-ante and with what lag.
- [ ] How far back forecasts are stored with their issue times (needed for all "change since day-ahead" variables).
- [ ] Availability of battery state-of-charge and BOA stack data.
- [ ] Sign convention for NIV in the source data (positive = short or long).