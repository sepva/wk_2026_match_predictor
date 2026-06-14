# Experiment Results — 2026-06-14

## Setup

- Dataset version: split_v2 (manifest: `data/processed/split_manifest.json`)
- Evaluation strategy: **Leave-One-Tournament-Out CV** over WC 2010 / 2014 / 2018 / 2022
- Per fold: train on all matches before that WC; eval on that WC's 64 matches (strict temporal ordering)
- Pooled eval: 4 × 64 = **256 matches** — 95% CI width ~0.4 pts
- Primary metric: mean Sporza group-stage points per match (max 10); bootstrap 95% CI (n=10,000)
- Autofill baseline: **measured empirically** — 4.137 pts/match
- Tracking: MLflow experiment `wk2026-tabular-2026-06-14`

## Cumulative leaderboard (all experiments to date)

| Approach | LOTO-CV mean | 95% CI | Δ vs autofill | Δ vs GLM | Notes |
|----------|:---:|:---:|:---:|:---:|---|
| **Autofill** (ELO-favourite 1-0 / 1-1) | **4.137** | [3.742, 4.539] | — | −0.199 | Empirical baseline |
| Random (Poisson marginal) | 2.936 | [2.869, 3.004] | −1.201 | −1.400 | True floor |
| ELO-only (zero params) | 3.961 | [3.582, 4.352] | −0.176 | −0.375 | No training |
| **Poisson GLM** (ELO + form) | **4.336** | [3.930, 4.742] | +0.199 | 0.000 | Best overall; current champion |
| Dixon-Coles ρ (on GLM λs) | 4.328 | [3.926, 4.734] | +0.191 | −0.008 | ρ negligible |
| Dixon-Coles full MLE (αᵢ/δⱼ) | 3.762 | [3.383, 4.141] | −0.375 | −0.574 | Worse than autofill; per-team overfitting |
| Bayesian hierarchical Poisson (Exp A) | 4.270 | [3.887, 4.660] | +0.133 | −0.066 | Fixes sparse-fold; loses form features |
| **Reg GLM + team dummies (Exp B)** | **4.379** | [3.969, 4.781] | **+0.242** | **+0.043** | New best; team dummies with L2 add marginal signal |

## Experiment B: Regularised GLM with L2-penalised Team Dummies

### Per-fold results

| Fold | mean_pts | exact | correct | best_alpha | Δ vs GLM |
|------|:--------:|:-----:|:-------:|:----------:|:--------:|
| WC 2010 | 4.312 | 18.8% | 53.1% | 0.1 | +0.171 |
| WC 2014 | 4.594 | 12.5% | 60.9% | 0.001 | −0.281 |
| WC 2018 | 4.750 | 21.9% | 59.4% | 0.001 | +0.188 |
| WC 2022 | 3.859 | 7.8% | 56.2% | 0.001 | +0.093 |
| **Pooled** | **4.379** | — | — | — | **+0.043** |

### Interpretation

**Outcome B: Team dummies ≈ GLM baseline (+0.043 pts, CI overlaps).** The gain is real in 3 of 4
folds but the large 2014 regression (−0.281) drags the pooled mean. The CI overlap means the
improvement is not statistically conclusive.

Key observations:
- **2010 fold (most sparse, 219 rows/132 teams):** +0.171 pts with alpha=0.1. Heavier regularisation
  correctly suppresses the team dummies in the sparse setting where the GLM's aggregate features
  dominate.
- **2014 fold regression (−0.281):** alpha=0.001 (very low penalty) was selected by inner CV — the
  model is fitting team-specific patterns on the 2014 training set that generalise poorly to the
  actual 2014 WC. This is the main failure mode: inner CV selects near-zero regularisation when
  training data is larger, allowing overfitting.
- **2018 and 2022:** team dummies help (+0.188, +0.093) with near-zero alpha, suggesting that once
  enough data exists (~7k+ training rows), team identity adds real signal beyond ELO.

**Root cause of 2014 regression:** The inner CV minimises Poisson deviance (log-likelihood), not
Sporza score. With 3,900 training rows (2014 fold), the model has enough capacity to memorise
team-specific λ offsets that minimise training deviance but don't transfer to the WC score
distribution. A higher alpha floor or Sporza-score-based inner CV would address this.

### Decision

Team dummies carry **marginal** signal but the regularisation strategy needs fixing before this
approach is worth pursuing further. Options:

1. **Add a minimum alpha floor** (e.g. alpha ≥ 0.1 always) to prevent near-zero regularisation in
   larger folds — this is a 30-minute fix that could recover the 2014 regression.
2. **Move to Experiment C (pi-ratings)** — a drop-in ELO replacement that adds score-margin signal
   without the team-dummy overfitting risk.
3. **Move to Experiment D (squad age)** or **E (Transfermarkt bias correction)** — orthogonal
   features that don't interact with the team-dummy issue.

## MLflow run IDs

| Approach | MLflow experiment | Run ID |
|----------|-------------------|--------|
| Reg GLM + team dummies (Exp B) | `wk2026-tabular-2026-06-14` | `6ea4089d71e34b93866e0faed0a0fc5d` |
