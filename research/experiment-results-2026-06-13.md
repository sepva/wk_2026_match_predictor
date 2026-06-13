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

> **The Poisson GLM remains the strongest model; Dixon-Coles adds no meaningful improvement.**
> DC 4.328 vs GLM 4.336 is −0.008 pts/match — within noise. The ρ correction did not deliver the
> expected +0.3–0.5 pts gain because the per-fold ρ values are very small, meaning the training data
> does not show a strong systematic excess/deficit in low-score outcomes relative to independent Poisson.
> Both models beat autofill (4.137) by ~+0.20 pts but the gap is not yet statistically conclusive.

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

1. **Full Dixon-Coles** (team-specific attack/defence parameters, not just ρ on GLM λs) — fitting αᵢ/δⱼ per team via MLE rather than using a GLM with aggregate features. This is the original Dixon-Coles formulation and captures team-level heterogeneity the GLM cannot.
2. **WC 2010 training data starvation** — the 2010 fold only has 219 training rows (vs 11,106 for 2022). The model likely has high variance there. Using all-tournament training (including 2022 for inference) will help.
3. **Better features** — current form features are simple win-rate/goal averages; xG, head-to-head, or squad strength (Transfermarkt/SPI) may add signal.

## Winner (for this round)

**Poisson GLM** — highest LOTO-CV mean. Dixon-Coles ρ-only is not an improvement.

## MLflow run IDs (LOTO-CV runs)

| Approach | Run ID |
|----------|--------|
| random_poisson | see MLflow `wk2026-tabular-2026-06-13` run `random_poisson_loto` |
| elo_only | `elo_only_loto` |
| poisson_glm | `poisson_glm_loto` |
| dixon_coles | `e30c2f2acf8448a08f218b7aeb6b5298` |
