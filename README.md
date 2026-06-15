# WK 2026 Match Predictor

A machine learning system to predict match outcomes for the 2026 FIFA World Cup, built to compete in the [Sporza WK-pronostiek](https://wkpronostiek.sporza.be) minicompetition.

## Goal

Predict exact scores (home goals, away goals) for all 104 WC 2026 matches to maximise expected Sporza points. The scoring system rewards exact scores (10 pts) and correct goal differences (7 pts) over simple win/draw/loss predictions, so the core modelling target is a Poisson rate pair (λ_home, λ_away) rather than a classifier.

## Approach

Poisson regression family — models predict team-level attack/defence parameters and derive full score distributions. The submitted prediction is the score that maximises expected Sporza points under that distribution.

### Experiments (best to date)

| Exp | Model | CV pts/match |
|-----|-------|-------------|
| A | Bayesian hierarchical Poisson (PyMC) | 4.270 |
| B | Regularised GLM with team dummies | 4.379 |
| B-fixed | Regularised GLM, fixed α | 4.344 |
| C | Pi-Ratings GLM | 4.375 |
| D | Hybrid ELO + Pi-Ratings GLM | **4.387** |
| E | Live-update CV test | +0.043 (neutral) |

Current best model: **Exp D — Hybrid ELO + Pi-Ratings GLM** (4.387 pts/match).

## Stack

- **Language:** Python 3.13
- **Core libs:** `penaltyblog`, `scikit-learn`, `PyMC`, `pandas`, `numpy`
- **Experiment tracking:** MLflow (local SQLite)
- **Data versioning:** DVC
- **Notebooks:** Jupyter, organised under `notebooks/`
- **Automation:** `scripts/push_sporza.py` — daily prediction push to Sporza API

## Project Structure

```
notebooks/
  data_cleaning/    # 07: cleaning pipeline
  eda/              # 01–06: EDA across match results, ELO, FIFA rankings, player ratings
  models/           # 08–21: train/test split → baselines → full model experiments
  generation/       # 20: WC 2026 prediction generation
src/
  features/         # feature engineering
  models/           # model implementations
  evaluation/       # scoring utilities
  sporza_client.py  # Sporza API client
scripts/
  push_sporza.py    # daily automation: push predictions to Sporza
data/
  raw/              # source datasets
  processed/        # cleaned/feature-engineered data
  predictions/      # generated WC 2026 predictions CSV
reports/            # EDA, data quality, feature engineering write-ups
context/            # project brief, preferences, handoff notes
```

## Quickstart

```bash
uv sync
jupyter lab
```

Run notebooks in order within each subfolder. Start with `notebooks/eda/` for data exploration, then `notebooks/models/` for experiments, then `notebooks/generation/20_generate_wc2026_predictions.ipynb` to regenerate predictions.

## Status

Tournament started June 12, 2026. Group stage in progress. Predictions are being updated before each match day using the current best model + live fixture results.
