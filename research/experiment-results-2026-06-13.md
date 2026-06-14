# Experiment Results — 2026-06-13

## Setup

- Dataset version: split_v2 (manifest: `data/processed/split_manifest.json`)
- Evaluation strategy: **Leave-One-Tournament-Out CV** over WC 2010 / 2014 / 2018 / 2022
- Per fold: train on all matches before that WC; eval on that WC's 64 matches (strict temporal ordering)
- Pooled eval: 4 × 64 = **256 matches** — 95% CI width ~0.4 pts (vs ~1.4 pts at n=64)
- Primary metric: mean Sporza group-stage points per match (max 10); bootstrap 95% CI (n=10,000)
- Autofill baseline: **measured empirically** — predict 1-0 to ELO-favourite, 1-1 if |elo_diff|<50
- Tracking: MLflow experiment `wk2026-tabular-2026-06-13`

## Results

| Approach | LOTO-CV mean | 95% CI | WC 2022 (most recent) | Notes |
|----------|:---:|:---:|:---:|---|
| **Autofill** (ELO-favourite 1-0 / 1-1) | **4.137** | [3.742, 4.539] | — | Empirically measured; was *assumed* ~5 pts before |
| Random (Poisson marginal) | 2.936 | [2.869, 3.004] | 2.949 | True floor |
| ELO-only (zero params) | 3.961 | [3.582, 4.352] | 4.266 | No training; pure ELO win-prob → floor(λ) |
| **Poisson GLM** (ELO + form) | **4.336** | [3.930, 4.742] | 3.766 | Best LOTO-CV; optimal Sporza score prediction |
| Dixon-Coles (ρ on GLM λs) | 4.328 | [3.926, 4.734] | 3.844 | ρ small negative (−0.02 to −0.04); negligible gain over GLM |
| Dixon-Coles full MLE (αᵢ/δⱼ per team) | 3.762 | [3.383, 4.141] | 2.922 | **Worse than autofill**; severe overfitting on sparse folds |
| **Bayesian hierarchical Poisson** (ELO hyperpriors) | **4.270** | [3.887, 4.660] | 3.719 | Fixed sparse-fold collapse (2010: 4.39 vs DC MLE's 2.92); −0.066 vs GLM |

> **The Poisson GLM remains the strongest model; full DC MLE is a step backwards; Bayesian hierarchical model is between the two.**
> DC MLE 3.762 vs GLM 4.336 is −0.574 pts/match. The per-team parameters overfit on sparse folds
> (only 219 training matches for 2010, 132 teams) — minnow teams (Turks and Caicos, Brunei) dominate
> the defence ranking because they concede rarely against other minnows, then drag predictions for
> WC teams badly wrong. WC 2022 fold collapses to 2.922 pts (below random floor at 2.936).
> The Bayesian hierarchical model (Experiment A) fixes the sparse-fold collapse (2010: 4.39 pts)
> but still lands 0.066 pts below the GLM pooled mean — the model loses the form features that
> drive GLM's advantage and the ELO-based hyperprior can't fully compensate.
> Both GLM variants beat autofill (4.137) by ~+0.20 pts but the gap is not yet statistically conclusive.

## Key corrections vs prior run

1. **Autofill target corrected**: previous assumption of ~5 pts/match was fabricated. Empirical measurement gives **4.14 pts/match** [3.74, 4.54] for the 1-0/1-1 ELO-heuristic on the same 256 eval matches. The bar is lower than assumed — and the Poisson GLM is already close.

2. **Evaluation methodology fixed**: replaced static 192/64 val/test with LOTO-CV (256 pooled matches). CI width reduced from ±0.68 pts (n=64) to ±0.41 pts (n=256). Prior results were within each other's noise bands; current results are more trustworthy.

3. **ELO-only was overstated on test**: the previous run showed ELO-only at 4.27 on WC 2022 which looked good, but LOTO-CV reveals it's only 3.96 pooled — WC 2022 was just a lucky fold for ELO-only.

## Autofill breakdown (empirical)

| WC | Autofill pts/match |
|----|--------------------|
| 2010 | see notebook 08 |
| 2014 | see notebook 08 |
| 2018 | see notebook 08 |
| 2022 | see notebook 08 |
| **Pooled** | **4.137** [3.742, 4.539] |

## Gap analysis

The Poisson GLM is +0.20 pts/match above autofill (not yet significant). Dixon-Coles did not widen this gap — ρ values are too small to matter.

Why ρ was small: the GLM already absorbs mean goal rates well; the residual correlation between home and away goals in WC data is not large enough for ρ to make a material difference.

Remaining levers most likely to open the gap:

1. ~~**Full Dixon-Coles** (team-specific attack/defence parameters)~~ — **tried and failed** (notebook 13). Per-team MLE overfits severely on sparse data; minnow teams corrupt the defence estimates. The GLM's aggregate features (ELO, form) are better regularisers than raw per-team parameters without explicit shrinkage.
2. **Regularised / hierarchical Dixon-Coles** — fit per-team parameters with L2 shrinkage (or a Bayesian prior towards the mean). This is the correct fix for the overfitting problem identified in notebook 13.
3. **WC 2010 training data starvation** — the 2010 fold only has 219 training rows (vs 11,106 for 2022). The model likely has high variance there. Using all-tournament training (including 2022 for inference) will help.
4. **Better features** — current form features are simple win-rate/goal averages; xG, head-to-head, or squad strength (Transfermarkt/SPI) may add signal.

## Winner (for this round)

**Poisson GLM** — highest LOTO-CV mean. Dixon-Coles ρ-only is not an improvement.

## MLflow run IDs (LOTO-CV runs)

| Approach | Run ID |
|----------|--------|
| random_poisson | see MLflow `wk2026-tabular-2026-06-13` run `random_poisson_loto` |
| elo_only | `elo_only_loto` |
| poisson_glm | `poisson_glm_loto` |
| dixon_coles | `e30c2f2acf8448a08f218b7aeb6b5298` |
