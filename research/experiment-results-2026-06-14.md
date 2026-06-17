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
| **Poisson GLM** (ELO + form) | **4.336** | [3.930, 4.742] | +0.199 | 0.000 | Best stable model |
| Dixon-Coles ρ (on GLM λs) | 4.328 | [3.926, 4.734] | +0.191 | −0.008 | ρ negligible |
| Dixon-Coles full MLE (αᵢ/δⱼ) | 3.762 | [3.383, 4.141] | −0.375 | −0.574 | Worse than autofill; per-team overfitting |
| Bayesian hierarchical Poisson (Exp A) | 4.270 | [3.887, 4.660] | +0.133 | −0.066 | Fixes sparse-fold; loses form features |
| Reg GLM + team dummies (Exp B) | 4.379 | [3.969, 4.781] | +0.242 | +0.043 | 2014 fold regression from near-zero alpha |
| Reg GLM + team dummies, alpha≥0.1 (Exp B-fixed) | 4.344 | [3.945, 4.750] | +0.207 | +0.008 | Fixes 2014 but caps signal in larger folds |
| **Pi-Ratings GLM (Exp C)** | **4.375** | [3.977, 4.781] | **+0.238** | **+0.039** | Drop-in ELO replacement; good 2014/2018; 2022 regression |
| **Hybrid ELO+Pi GLM (Exp D)** | **4.387** | [3.984, 4.789] | **+0.250** | **+0.051** | Best model; 3/4 folds improve; stable across all folds |
| Live-update CV (Exp E) | 4.324 | [3.922, 4.719] | +0.187 | +0.012 | Static 4.281 vs live 4.324; +0.043 delta within noise |
| Stacked calibration (Exp 22, first pass) | 4.422 | [4.019, 4.824] | +0.285 | +0.035 vs Exp D | Large 2022 uplift (+0.453) but hurt 2014/2018; p=0.400 |
| **Robust stacked calibration (Exp 22b)** | **4.441** | [4.031, 4.848] | **+0.305** | **+0.055 vs Exp D** | Conservative gating reduced collateral damage; 2022 +0.203; still 2018 −0.125; p=0.216 |

> **Hybrid ELO+Pi GLM (Exp D) remains the best stable default.** Exp 22b reaches a higher pooled mean (4.441) but does not yet clear significance against Exp D (paired permutation p=0.216) and still regresses WC2018. Stacking is currently best treated as a conditional correction layer rather than a full replacement model.

---

## Experiment B: Regularised GLM with L2-penalised Team Dummies

### Per-fold results

| Fold | mean_pts | exact | correct | best_alpha | Δ vs GLM |
|------|:--------:|:-----:|:-------:|:----------:|:--------:|
| WC 2010 | 4.312 | 18.8% | 53.1% | 0.1 | +0.171 |
| WC 2014 | 4.594 | 12.5% | 60.9% | 0.001 | −0.281 |
| WC 2018 | 4.750 | 21.9% | 59.4% | 0.001 | +0.188 |
| WC 2022 | 3.859 | 7.8% | 56.2% | 0.001 | +0.093 |
| **Pooled** | **4.379** | — | — | — | **+0.043** |

### Experiment B-fixed (alpha floor ≥ 0.1)

| Fold | mean_pts | exact | correct | best_alpha | Δ vs B | Δ vs GLM |
|------|:--------:|:-----:|:-------:|:----------:|:------:|:--------:|
| WC 2010 | 4.312 | 18.8% | 53.1% | 0.1 | +0.000 | +0.171 |
| WC 2014 | 4.734 | 17.2% | 62.5% | 0.1 | +0.140 | −0.141 |
| WC 2018 | 4.562 | 18.8% | 57.8% | 0.1 | −0.188 | +0.000 |
| WC 2022 | 3.766 | 7.8% | 54.7% | 0.1 | −0.093 | −0.000 |
| **Pooled** | **4.344** | — | — | — | **−0.035** | **+0.008** |

**Conclusion:** The alpha floor fixed the 2014 regression (+0.140) but cost signal in 2018 (−0.188) and 2022 (−0.093). The inner CV's low-alpha preference on large folds was capturing genuine per-team signal, not just overfitting — only 2014 was a true overfit case. No single alpha value works well across all fold sizes. Team dummies are ruled out as a reliable improvement strategy.

---

## Experiment C: Pi-Ratings GLM

Pi-ratings (penaltyblog `PiRatingSystem`) computed from full match history back to 1990, strictly temporal (no leakage). Replace `elo_home`, `elo_away`, `elo_diff` with `pi_home`, `pi_away`, `pi_diff`. All form features kept identical.

### Per-fold results

| Fold | mean_pts | exact | correct | Δ vs GLM |
|------|:--------:|:-----:|:-------:|:--------:|
| WC 2010 | 4.266 | 20.3% | 51.6% | +0.125 |
| WC 2014 | 4.969 | 18.8% | 64.1% | +0.094 |
| WC 2018 | 4.797 | 20.3% | 60.9% | +0.235 |
| WC 2022 | 3.469 | 6.2% | 50.0% | −0.297 |
| **Pooled** | **4.375** | — | — | **+0.039** |

**95% CI:** [3.977, 4.781]  
**Permutation test p-value (Pi > ELO GLM):** 0.398 — not significant.

### Interpretation

Pi-ratings outperform ELO in 3 of 4 folds (2010: +0.125, 2014: +0.094, 2018: +0.235) but the WC 2022 fold collapses badly (3.469, −0.297 vs GLM). The 2022 regression is the critical question: is it noise, or does it reveal a systematic pi-ratings weakness?

Likely cause of 2022 regression: pi-ratings weight recent goal-margin performance heavily. In the 2022 cycle, teams may have played differently in qualifying vs WC (defensive tactics, squad rotation), causing the high-pi teams to underperform their rating at the tournament. ELO's recency-insensitive averaging is more robust to this mismatch.

**Pre-WC-2022 sanity check on ratings:** Brazil +3.66, Argentina +3.23, Germany +2.59, France +2.46 — sensible ordering.

**Decision:** Pi-ratings do not reliably beat the ELO GLM. The 2022 regression is too large to accept (+0.039 pooled masks a −0.297 hit on the most recent WC). For actual WC 2026 predictions, reverting to ELO GLM is safer.

**One possible next step:** Hybrid feature — use both `elo_diff` AND `pi_diff` as features in the same GLM, letting the model learn the weight. This costs nothing (same pipeline, one extra feature) and may capture the best of both signals without fully committing to pi-ratings.

---

---

## Experiment E: Live-Update CV Test

Tests whether the per-matchday feature update mechanism in the generation notebook (pi-ratings and form recomputed from played WC results) improves LOTO-CV score vs. static pre-tournament snapshots.

### Per-fold results

| Fold | Static | Live-update | Delta |
|------|:------:|:-----------:|:-----:|
| WC 2010 | 4.156 | 4.156 | +0.000 |
| WC 2014 | 4.562 | 4.969 | +0.406 |
| WC 2018 | 4.656 | 4.594 | −0.062 |
| WC 2022 | 3.750 | 3.578 | −0.172 |
| **Pooled** | **4.281** | **4.324** | **+0.043** |

**95% CI static:** [3.887, 4.680]  
**95% CI live-update:** [3.922, 4.719]

**Conclusion:** The live-update mechanism is approximately neutral (+0.043 pts/match, CIs fully overlap). WC 2014 benefits meaningfully (+0.406) but WC 2022 declines (−0.172). The effect does not replicate consistently across folds — noise at 64 matches per tournament. The mechanism is correct to keep in the generation notebook (ensures features reflect current tournament state) but should not be expected to systematically improve predictions.

---

## MLflow run IDs

| Approach | MLflow experiment | Run ID |
|----------|-------------------|--------|
| Reg GLM + team dummies (Exp B) | `wk2026-tabular-2026-06-14` | `6ea4089d71e34b93866e0faed0a0fc5d` |
| Reg GLM + team dummies, alpha≥0.1 (Exp B-fixed) | `wk2026-tabular-2026-06-14` | `7c0aaaee0b824205b6497ca86e21d8c0` |
| Pi-Ratings GLM (Exp C) | `wk2026-tabular-2026-06-14` | `dd71d64213b24f799f5388bce8bc7587` |
