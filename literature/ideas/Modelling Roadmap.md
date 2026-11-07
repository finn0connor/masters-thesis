---
type: idea
created: 2026-10-24
status: open
tags: [idea, modelling, forecasting]
---
# Modelling Roadmap

> [!summary] Overview
> - Progression: non-ML baselines, then machine learning, then neural networks. Every model is scored against the baselines.
> - Targets: NIV and the imbalance price (PIMB), forecast at the four auction runs (DA, IDA1, IDA2, IDA3).
> - The forecasting models later become the surrogates for the sensitivity analysis.

## 1. Framing

- **Two-step structure (NIV, then price).** The Irish PIMB is set by the most expensive balancing action needed to resolve the NIV, plus flagging and tagging. So the price is roughly a function of NIV and the balancing cost stack. Bottieau (Belgium), Plakas (Greece) and Browell and Gilbert (GB) all use some form of "forecast the imbalance, then map it to a price". This chain (inputs, then NIV, then price) is also the bridge to the sensitivity analysis.
- **Expect low skill at these horizons.** In GB, Browell and Gilbert found day-ahead imbalance price forecasts improved on climatology by only about 3%, against 5-40% for intraday (mostly under 3 hours ahead). The DA and IDA1 runs are 6-36 hours ahead, so small gains over a strong baseline are a valid result. Skill should increase towards gate closure across the four runs.

## 2. Setup Decisions

- **Model the PIMB - DA spread rather than raw PIMB.** This removes the gas-driven price level (relevant given the 2022 energy crisis in the data window) and matches the P95/P99 rare-event definition.
- **Add the last known NIV and PIMB at run time as features**, using the same as-of logic as the slow series. Persistence is the strongest single predictor in most NIV studies and is not yet in the pipeline.

## 3. Stage 1: Non-ML Models

| Model                                     | Description                                                                                                                           | Purpose                                                                                                                                                                     |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Naive benchmarks                          | NIV = 0, last known NIV, same period yesterday or last week. Price: PIMB = DA price (spread = 0)                                      | Reference for relative MAE. Narajewski used the intraday price as the naive benchmark for German imbalance prices                                                           |
| Climatology                               | Mean NIV or spread by hour of day and month, or a rolling 4-week profile                                                              | The rolling version adapts to level shifts such as the 2025-26 NIV bias                                                                                                     |
| LEAR                                      | LASSO-regularised linear regression, refitted on a rolling window (Lago et al.)                                                       | Main benchmark. O'Connor 2024 found LEAR outperformed deep learning on the Irish balancing market (MAE 32.82 EUR/MWh). Interpretable, gives direct sensitivities            |
| ARX / SARIMAX                             | Autoregressive model with exogenous inputs, often one model per settlement period                                                     | Classical time-series standard; isolates the value of autoregressive structure                                                                                              |
| Two-step structural model                 | Fit spread = g(NIV) as a piecewise or isotonic curve, separately for long and short systems, then input an NIV forecast               | Follows Browell's day-ahead approach (separate long and short distributions weighted by the probability of a short system). Represents the physical chain needed for the SA |
| Regime switching and jumps (from finance) | Markov-switching AR (calm and stressed regimes), or a mean-reverting process with jumps as used for spot power                        | Spikes behave as a separate regime rather than the tail of one distribution. The stressed-regime probability is a useful output                                             |
| Quantile and logistic regression          | Linear models for P90/P95/P99, logistic regression for P(spread > P95) and for long vs short                                          | Direct linear baseline for rare events                                                                                                                                      |
| Extreme value theory                      | Peaks-over-threshold with a generalised Pareto fit to spread exceedances above P95, optionally with covariates in the scale parameter | Tail-risk analogue of value-at-risk and expected shortfall. pyextremes is already installed                                                                                 |

## 4. Stage 2: Machine Learning

- **Gradient boosting (XGBoost, LightGBM).** Tune on time-ordered validation folds. Quantile objectives for P10/P50/P90/P99; NGBoost or XGBoost distributional mode for full distributions.
- **Quantile regression forest.** Plakas used a QRF for system imbalance followed by gradient boosting with Markov switching for price. Replicate this two-stage design on Irish data.
- **Spike classifier.** Gradient-boosted classifier for P(spread > P95) with class weights. Evaluate with precision, recall and Brier score.
- **Conformal prediction.** Wraps any point model to produce calibrated intervals; adaptive variants handle regime shifts in time series.
- **SHAP values** for model interpretation. Keep these distinct from the sensitivity analysis: SHAP explains one model's predictions, whereas global SA works on input distributions.

## 5. Stage 3: Neural Networks

- **MLP / DNN.** The Lago et al. benchmark DNN, available in the epftoolbox library. Start here as the published reference.
- **NBEATSx / NHITS** (neuralforecast library). Handle exogenous inputs and perform strongly in recent price forecasting benchmarks.
- **Temporal Fusion Transformer.** Quantile outputs and attention-based interpretability; heavy for the available data size.
- **Distributional neural networks.** The network outputs parameters of a Student-t or Johnson SU distribution (Marcjasz, Narajewski, Weron and Ziel). Well suited to heavy-tailed spreads.
- **LSTM / GRU.** Used in the UK NIV study; include as a comparison rather than the main model.

> [!warning] Data size
> 2022-2026 gives roughly 80,000 half-hours per run, which is small for deep learning, and the Irish evidence (O'Connor 2024) favours LEAR. Include one or two neural networks and report honestly whether they help.

## 6. Evaluation

- **Walk-forward evaluation** with weekly or monthly refitting, replacing the single 80/20 split. The test period contains Greenlink, the 30-minute DA change and SDP-02 battery dispatch (Nov 2025), so a model frozen at the 80% point is tested on a different market.
- **Point accuracy:** MAE, RMSE, relative MAE against the naive benchmark, and direction accuracy for NIV (long vs short drives price formation).
- **Probabilistic accuracy:** pinball loss and CRPS.
- **Tail accuracy:** MAE on P95+ events, plus precision, recall and Brier score for the spike classifier.
- **Significance:** Diebold-Mariano tests between pairs of models.

## 7. Link to the Sensitivity Analysis

- The forecasting models act as surrogates g(x), sampled thousands of times by the SA.
- **Use a small set of physical inputs for the SA (around 8-15):** wind forecast error, demand error, interconnector schedule, outages, battery availability, DA price. Not the full feature set.
- **Inputs are correlated** (wind with demand, wind with interconnector flows), so standard Sobol indices are misleading. Use Shapley effects or copula-based sampling.
- **Surrogate properties differ:**
  - LEAR gives analytic sensitivities.
  - Gradient boosting is fast but piecewise constant: suitable for sampling-based Sobol and extreme-oriented SA, not gradient-based methods.
  - Neural networks are differentiable.
  - PCE (Shang et al. 2024) can be fitted to the inputs and outputs of the best model.
- **Validate every surrogate on extreme periods** before trusting its sensitivity results.

## 8. Order of Work

1. **Before the interim report (20 Nov 2026):** walk-forward evaluation, lagged NIV and price features, naive benchmarks, climatology and LEAR, compared with XGBoost across the four runs.
2. **Next:** two-step NIV-to-spread model, quantile gradient boosting and QRF, spike classifier, POT/GPD tail fit.
3. **Then:** one or two neural networks (MLP or distributional NN, plus NBEATSx), tested for significance against LEAR and gradient boosting.
4. **Finally:** select the best two or three models as surrogates and run average-based, extreme-oriented and threshold-based SA.

## References

- Browell, J. and Gilbert, C. (2022). Predicting electricity imbalance prices and volumes: capabilities and opportunities. Energies 15(10), 3645. https://strathprints.strath.ac.uk/80742/
- Bottieau, J. et al. Probabilistic forecasting of imbalance prices in the Belgian context. https://arxiv.org/abs/2106.07361
- Short term net imbalance volume forecasting through machine and deep learning: a UK case study. https://dl.ifip.org/hal-03789014v1
- Olivares, K. et al. NBEATSx: neural basis expansion analysis with exogenous variables. https://arxiv.org/abs/2104.05522
- Lago, J. et al. (2021). Forecasting day-ahead electricity prices: a review of state-of-the-art algorithms, best practices and an open-access benchmark. https://arxiv.org/abs/2008.08004
- Marcjasz, G., Narajewski, M., Weron, R. and Ziel, F. (2023). Distributional neural networks for electricity price forecasting. Energy Economics. (not yet in library)
- In library: oconnor2024, narajewski2022, plakas2025, lucas2020, weron2014, lago2021, shang2024, singh2026.
