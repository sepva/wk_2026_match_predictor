# Feature Engineering Report — 2026-06-13

## Feature inventory

| Feature | Type | Transform | Owner | Rationale | Available at serving? |
|---------|------|-----------|-------|-----------|----------------------|
| `home_elo` | numeric | StandardScaler | ELO history (eloratings.net) | Pre-match team strength — strongest single predictor per EDA correlation analysis | ✅ (WC2026 snapshot) |
| `away_elo` | numeric | StandardScaler | ELO history (eloratings.net) | Pre-match team strength — away side | ✅ |
| `elo_diff` | numeric | StandardScaler | Derived | Sign-consistent team strength gap; EDA showed monotonic win-rate gradient across quintiles (8%→79%) | ✅ |
| `home_form_wr` | numeric | StandardScaler | Rolling form (matches.parquet) | Win rate over last 5 matches — captures momentum independent of absolute ELO level | ✅ |
| `away_form_wr` | numeric | StandardScaler | Rolling form | Same for away team | ✅ |
| `form_diff_wr` | numeric | StandardScaler | Derived | form_home − form_away | ✅ |
| `home_form_gf` | numeric | StandardScaler | Rolling form | Goals scored per match (last 5) — proxy for attacking output | ✅ |
| `away_form_gf` | numeric | StandardScaler | Rolling form | Goals scored per match (last 5) | ✅ |
| `form_diff_gf` | numeric | StandardScaler | Derived | Goals scored diff | ✅ |
| `home_form_ga` | numeric | StandardScaler | Rolling form | Goals conceded per match (last 5) — proxy for defensive quality | ✅ |
| `away_form_ga` | numeric | StandardScaler | Rolling form | Goals conceded per match (last 5) | ✅ |
| `home_log_mv` | numeric | StandardScaler (+ median impute) | Transfermarkt squad_values.parquet | log(sum top-23 market values) — squad quality proxy; Feb 2026 snapshot | ✅ (WC2026 squads only) |
| `away_log_mv` | numeric | StandardScaler (+ median impute) | Transfermarkt | Same for away side | ✅ |
| `log_mv_diff` | numeric | StandardScaler (+ median impute) | Derived | Squad value gap | ✅ |
| `tournament_weight` | numeric | StandardScaler | Match metadata | Competition importance (1=friendly, 2=qualifier, 3=major tournament) — controls for how hard teams try | ✅ |
| `is_neutral` | binary (int) | StandardScaler | Match metadata | 1 if neutral venue — removes home-field advantage bias; all WC2026 matches are neutral | ✅ |

**Total features: 16**

## Pipeline structure

```
ColumnTransformer
└── "num": Pipeline(SimpleImputer(median) → StandardScaler)
    └── all 16 numeric features (NUMERIC_FEATURES)
```

- No categorical features in Phase 1 — team identity captured via ELO, not one-hot
- Squad value features (home_log_mv, away_log_mv, log_mv_diff) are imputed with median; they are NaN for ~67–87% of historical training rows but 0% missing in WC2026 prediction set
- Entry point: `src/features/pipeline.py::build_pipeline(model)` — returns a ready-to-fit `sklearn.pipeline.Pipeline`

## Training data

- **Source**: `data/interim/matches.parquet` joined with `elo_history.parquet`, `squad_values.parquet`
- **Date range**: 2010-01-02 → 2026-06-11
- **Rows**: 14,681 matches (restricted to teams present in ELO history; drops ~7.2% non-FIFA teams)
- **Output file**: `data/interim/train_features.parquet`

## WC 2026 prediction data

- **Source**: `data/interim/wc2026_fixtures.parquet` (72 group-stage fixtures with resolved team names)
- **ELO source**: `elo_wc2026.parquet` (pre-tournament snapshot, 0% stale)
- **Form source**: rolling window computed over full match history, state taken as of latest match per team
- **Squad values**: `squad_values.parquet` (Feb 2026 Transfermarkt, 0% missing for WC2026 teams)
- **Output file**: `data/interim/wc2026_features.parquet`

## Dropped features

| Feature | Reason |
|---------|--------|
| FIFA rankings | 722 days stale as of June 2026 — dominantly captured by ELO which is more predictive (per research) |
| FiveThirtyEight SPI | Discontinued June 2023 — useful only as historical calibration reference |
| city / country | Match venue details — subsumed by `is_neutral`; venue-specific effects too sparse to model |
| tournament (string) | Replaced by `tournament_weight` ordinal; one-hot encoding would add >190 sparse features with no benefit at this scale |
| raw squad_mv_sum_top23 | Replaced by log transform (right-skewed distribution per EDA) |
| individual player ratings | SofIFA 5.2 GB file deferred by user; squad-level market value captures aggregate quality |

## Null rate summary (training data)

| Feature group | Null rate |
|--------------|-----------|
| ELO features (home_elo, away_elo, elo_diff) | ~1–2% (teams with no ELO before first match) |
| Form features (win rate, goals) | ~0.7–1.2% (teams with very short match history) |
| Squad value features (log_mv_*) | ~67–87% (Transfermarkt only covers WC2026 squads) |
| tournament_weight, is_neutral | 0% |

## Feature store candidates

None for Phase 1 — features are computed at inference time from parquet files.
If serving latency matters in future: register `home_elo`, `away_elo`, `home_log_mv`, `away_log_mv` as pre-computed team features in Azure ML Feature Store, updated after each ELO release.

## Sanity check results

Baseline Poisson model trained on training features:
- Mean predicted home goals: 1.580 (actual: 1.580) ✅
- ELO diff quintile vs win rate: 8% → 22% → 40% → 66% → 79% ✅ (strong monotonic signal)
- Sample WC 2026 prediction: Mexico 2.04 – 0.64 South Africa (actual: 2–0) ✅

## Recommended next step

`/ds-build` — train a Dixon-Coles / Poisson regression baseline on the engineered features, evaluate on a held-out historical WC validation set, and establish the mean Sporza pts/match baseline.
