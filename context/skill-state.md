# Skill State

## Run log

| Date | Skill | Artifacts produced | Summary |
|---|---|---|---|
| 2026-06-12 | `/ds-start` | `context/project.md` | New project scaffolded — WK 2026 Match Predictor, solo project, mixed tabular + LLM, local-first then Azure |
| 2026-06-12 | `/ds-goals` | `context/project.md` (updated), `reports/goals-alignment-2026-06-12.md` | Goals defined: mean Sporza pts/match on held-out WC validation set; target: beat FIFA-ranking autofill baseline; exact score prediction (Poisson/Dixon-Coles) identified as right technical formulation |
| 2026-06-12 | `/ds-research` | `research/method-survey-2026-06-12.md`, `research/approach-shortlist-2026-06-12.md` | Data sources identified: Mart Jürisoo (results), ELO Ratings (Kaggle), OpenFootball WC 2026 fixtures, SofIFA player ratings, Transfermarkt market values, official WC 2026 squad PDF; primary model: Dixon-Coles + ELO via penaltyblog; player features as Phase 2 enrichment |
| 2026-06-12 | `/ds-eda` | `notebooks/01_match_results_eda.ipynb`, `notebooks/02_elo_ratings_eda.ipynb`, `notebooks/03_wc2026_fixtures_results_eda.ipynb`, `notebooks/04_fifa_rankings_spi_eda.ipynb`, `notebooks/05_transfermarkt_eda.ipynb`, `notebooks/06_player_ratings_eda.ipynb` | All datasets downloaded and 6 EDA notebooks created: match results (Mart Jürisoo + PataterieData), ELO ratings (full history + WC2026 snapshot), WC2026 fixtures (OpenFootball JSON + Kaggle DB), FIFA rankings + SPI reference, Transfermarkt market values, SofIFA player ratings (FIFA 15-22) |
| 2026-06-12 | `/ds-eda` (re-run) | `reports/eda-2026-06-12.md` | Notebooks 01–05 executed (notebook 06 SofIFA deferred — 5.2 GB file); 8 red flags found: team name harmonization (9 WC teams missing from ELO by name), FIFA rankings stale (722 days), SPI discontinued, Transfermarkt valuations stale (906 days) + 37% missing market values, PataterieData overlap unverified, 70 missing score rows |
| 2026-06-12 | `/ds-data-quality` | `reports/data-quality-2026-06-12.md` | 8 red flags resolved: full name harmonization table built (ELO \xa0 fix, 9 ELO mismatches, 5 TM mismatches), 2 MJ duplicates identified, Moldova ELO=0 flagged, 70 null scores confirmed as future fixtures; TM coverage audit complete; 0 deferred |
| 2026-06-13 | `/ds-feature-engineering` | `reports/feature-engineering-2026-06-13.md`, `src/features/`, `data/interim/train_features.parquet`, `data/interim/wc2026_features.parquet` | 16 features created (ELO at-date, rolling form 5-match, log squad MV, tournament weight, is_neutral); training table 14,681 rows 2010+; WC2026 table 72 fixtures, 0% nulls; sklearn Pipeline scaffolded; Poisson sanity check passed (Mexico 2.04–0.64 South Africa, actual 2–0) |
| 2026-06-13 | `/ds-experiment` | `data/processed/train_fold_*.parquet`, `data/processed/eval_fold_*.parquet`, `data/processed/eval_pooled.parquet`, `data/processed/split_manifest.json`, `notebooks/models/08–11`, `research/experiment-results-2026-06-13.md`, `research/experiment-log.md`, `src/evaluation/sporza.py` | LOTO-CV (4×64=256 eval matches); autofill empirically measured at 4.14 pts/match (not assumed 5.0); random 2.94, ELO-only 3.96, Poisson GLM 4.34 [3.93–4.74]; GLM leads but CIs overlap autofill |
| 2026-06-13 | manual | `notebooks/models/12_dixon_coles.ipynb`, `research/experiment-results-2026-06-13.md` (updated) | Dixon-Coles ρ correction on top of GLM λs: 4.328 [3.926–4.734] vs GLM 4.336 — negligible difference. Per-fold ρ values are small negative (−0.02 to −0.04); ρ-only correction does not open gap vs autofill. Notebooks reorganised into `notebooks/models/`. |
| 2026-06-13 | `/ds-experiment` | `notebooks/models/13_dixon_coles_full_mle.ipynb`, `research/experiment-results-2026-06-13.md` (updated) | Full Dixon-Coles MLE (per-team αᵢ/δⱼ via L-BFGS-B, time decay φ=0.003): **3.762 [3.383–4.141]** — worse than autofill (4.137). WC2022 fold collapses to 2.922 pts. Root cause: overfitting on sparse folds (219 rows/132 teams for 2010); minnow teams corrupt defence estimates. MLflow upgraded to 3.x (mlflow.db SQLite). |
| 2026-06-13 | `/ds-research` | `research/method-survey-2026-06-13.md`, `research/approach-shortlist-2026-06-13.md` | Phase 2 research completed: Bayesian hierarchical Poisson with ELO hyperpriors identified as primary fix for per-team overfitting; regularised GLM (L2 team dummies) recommended as fast first experiment; pi-ratings and squad age as secondary features; LLMs and bivariate Poisson deprioritised |
| 2026-06-13 | `/ds-experiment` | `notebooks/models/14_bayesian_hierarchical_poisson.ipynb`, `research/experiment-results-2026-06-13.md` (updated), `research/experiment-log.md` (updated) | Experiment A — Bayesian hierarchical Poisson (PyMC 6, ELO hyperpriors, NUTS 1k draws, LOTO-CV): **4.270 [3.887, 4.660]** — beats autofill (+0.13) but −0.066 vs GLM. Sparse 2010 fold fixed (4.39 vs DC MLE 2.92). GLM remains winner; model lacks form features. |
| 2026-06-14 | `/ds-experiment` | `notebooks/models/15_regularised_glm_team_dummies.ipynb`, `research/experiment-results-2026-06-14.md`, `research/experiment-log.md` (updated) | Experiment B — Regularised GLM + L2 team dummies (PoissonRegressor + OHE, inner 3-fold CV, LOTO-CV): **4.379 [3.969, 4.781]** — new best (+0.043 vs GLM). 2014 fold regression (−0.281) due to inner CV selecting alpha≈0.001; CI overlaps GLM — not conclusive. Team dummies carry marginal signal but regularisation strategy needs alpha floor. |
| 2026-06-14 | `/ds-experiment` | `notebooks/models/16_regularised_glm_team_dummies_alphafixed.ipynb`, `notebooks/models/17_pi_ratings_glm.ipynb`, `research/experiment-results-2026-06-14.md` (updated), `research/experiment-log.md` (updated) | Exp B-fixed (alpha≥0.1): **4.344 [3.945, 4.750]** — fixes 2014 (+0.140) but costs 2018/2022; +0.008 vs GLM. Team dummies ruled out. Exp C pi-ratings: **4.375 [3.977, 4.781]** — 3/4 folds improve but 2022 collapses (3.469, −0.297); p=0.398. ELO GLM remains best stable model. |

## Artifact index

| Artifact | Path | Produced by | Date |
|---|---|---|---|
| project context | `context/project.md` | `/ds-goals` | 2026-06-12 |
| AE preferences | `context/ae-preferences.md` | `/ds-start` | 2026-06-12 |
| goals alignment report | `reports/goals-alignment-2026-06-12.md` | `/ds-goals` | 2026-06-12 |
| method survey | `research/method-survey-2026-06-12.md` | `/ds-research` | 2026-06-12 |
| approach shortlist | `research/approach-shortlist-2026-06-12.md` | `/ds-research` | 2026-06-12 |
| EDA notebook — match results | `notebooks/01_match_results_eda.ipynb` | `/ds-eda` | 2026-06-12 |
| EDA notebook — ELO ratings | `notebooks/02_elo_ratings_eda.ipynb` | `/ds-eda` | 2026-06-12 |
| EDA notebook — WC 2026 fixtures | `notebooks/03_wc2026_fixtures_results_eda.ipynb` | `/ds-eda` | 2026-06-12 |
| EDA notebook — FIFA rankings + SPI | `notebooks/04_fifa_rankings_spi_eda.ipynb` | `/ds-eda` | 2026-06-12 |
| EDA notebook — Transfermarkt | `notebooks/05_transfermarkt_eda.ipynb` | `/ds-eda` | 2026-06-12 |
| EDA notebook — SofIFA player ratings | `notebooks/06_player_ratings_eda.ipynb` | `/ds-eda` | 2026-06-12 |
| EDA report | `reports/eda-2026-06-12.md` | `/ds-eda` | 2026-06-12 |
| data quality report | `reports/data-quality-2026-06-12.md` | `/ds-data-quality` | 2026-06-12 |
| data cleaning notebook | `notebooks/07_data_cleaning.ipynb` | manual | 2026-06-12 |
| cleaned matches | `data/interim/matches.parquet` | `notebooks/07_data_cleaning.ipynb` | 2026-06-12 |
| cleaned ELO history | `data/interim/elo_history.parquet` | `notebooks/07_data_cleaning.ipynb` | 2026-06-12 |
| WC 2026 ELO snapshot | `data/interim/elo_wc2026.parquet` | `notebooks/07_data_cleaning.ipynb` | 2026-06-12 |
| squad market values | `data/interim/squad_values.parquet` | `notebooks/07_data_cleaning.ipynb` | 2026-06-12 |
| WC 2026 fixtures | `data/interim/wc2026_fixtures.parquet` | `notebooks/07_data_cleaning.ipynb` | 2026-06-12 |
| feature engineering report | `reports/feature-engineering-2026-06-13.md` | `/ds-feature-engineering` | 2026-06-13 |
| feature builder module | `src/features/build_features.py` | `/ds-feature-engineering` | 2026-06-13 |
| sklearn pipeline scaffold | `src/features/pipeline.py` | `/ds-feature-engineering` | 2026-06-13 |
| training feature table | `data/interim/train_features.parquet` | `/ds-feature-engineering` | 2026-06-13 |
| WC 2026 feature table | `data/interim/wc2026_features.parquet` | `/ds-feature-engineering` | 2026-06-13 |
| train/val/test splits | `data/processed/train.parquet`, `data/processed/val.parquet`, `data/processed/test.parquet` | `/ds-experiment` | 2026-06-13 |
| split manifest | `data/processed/split_manifest.json` | `/ds-experiment` | 2026-06-13 |
| Sporza scoring utility | `src/evaluation/sporza.py` | `/ds-experiment` | 2026-06-13 |
| split notebook | `notebooks/models/08_train_test_split.ipynb` | `/ds-experiment` | 2026-06-13 |
| random baseline notebook | `notebooks/models/09_baseline_random.ipynb` | `/ds-experiment` | 2026-06-13 |
| ELO-only baseline notebook | `notebooks/models/10_baseline_elo_only.ipynb` | `/ds-experiment` | 2026-06-13 |
| Poisson GLM baseline notebook | `notebooks/models/11_baseline_poisson_glm.ipynb` | `/ds-experiment` | 2026-06-13 |
| Dixon-Coles notebook | `notebooks/models/12_dixon_coles.ipynb` | manual | 2026-06-13 |
| Dixon-Coles full MLE notebook | `notebooks/models/13_dixon_coles_full_mle.ipynb` | `/ds-experiment` | 2026-06-13 |
| experiment results report | `research/experiment-results-2026-06-13.md` | `/ds-experiment` | 2026-06-13 |
| experiment log | `research/experiment-log.md` | `/ds-experiment` | 2026-06-13 |
| Bayesian hierarchical Poisson notebook | `notebooks/models/14_bayesian_hierarchical_poisson.ipynb` | `/ds-experiment` | 2026-06-13 |
| method survey (Phase 2) | `research/method-survey-2026-06-13.md` | `/ds-research` | 2026-06-13 |
| approach shortlist (Phase 2) | `research/approach-shortlist-2026-06-13.md` | `/ds-research` | 2026-06-13 |
| regularised GLM team dummies notebook | `notebooks/models/15_regularised_glm_team_dummies.ipynb` | `/ds-experiment` | 2026-06-14 |
| regularised GLM team dummies alpha-fixed notebook | `notebooks/models/16_regularised_glm_team_dummies_alphafixed.ipynb` | `/ds-experiment` | 2026-06-14 |
| pi-ratings GLM notebook | `notebooks/models/17_pi_ratings_glm.ipynb` | `/ds-experiment` | 2026-06-14 |
| experiment results (2026-06-14) | `research/experiment-results-2026-06-14.md` | `/ds-experiment` | 2026-06-14 |

## Recommended next steps

Last run: `/ds-experiment` on 2026-06-14 (Exp B-fixed + Exp C pi-ratings).
Suggested next: `/ds-experiment` — hybrid ELO+pi-ratings GLM: add `pi_diff` as an extra feature alongside `elo_diff` in the plain GLM (one-line change to feature matrix; model learns the weight). OR pivot to `/ds-evaluate` — generate actual WC 2026 group stage predictions using the ELO GLM (current best stable model) before remaining matches kick off.
Alternatives: Experiment D (squad age feature, `pct_prime_age` from FIFA squad data, 2h); Experiment E (Transfermarkt European bias correction, 1h).
