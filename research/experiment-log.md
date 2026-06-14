# Experiment Log

---

## Experiment — 2026-06-13

**Hypothesis**: A fitted Poisson model with ELO and form features will outperform both random guessing and a zero-parameter ELO-only predictor; even the simplest trained model should approach the Sporza autofill baseline (~5 pts/match).

**Approaches tested**: random Poisson marginal, ELO-only (zero params), Poisson GLM (ELO + form features)

**Result**: Poisson GLM wins on val (4.50 pts/match, 17.7% exact score). ELO-only more stable across val/test (3.73/4.27). None reach the 5.0 pt/match target. Autofill remains unbeaten.

**Decision**: Proceed to Dixon-Coles — the ρ low-score correction is the most likely single lever to close the gap, by improving draw probability and exact 1-0/0-1 accuracy.

**Next step**: `/ds-build` — implement Dixon-Coles with time decay using `penaltyblog`, evaluate on same val/test split.

---

## Experiment — 2026-06-13 (run 2)

**Hypothesis**: Full Dixon-Coles MLE (per-team αᵢ/δⱼ parameters via L-BFGS-B + time decay) will capture team heterogeneity the GLM cannot and beat the Poisson GLM (4.336 pts/match).

**Approaches tested**: Dixon-Coles full MLE (notebook 13) — vectorised log-likelihood, time decay φ=0.003, identifiability via fixed α₀=0

**Result**: 3.762 pts/match [3.383, 4.141] — **worse than autofill (4.137) and random baseline (2.936)**. WC2022 fold: 2.922 pts, 4.7% exact, 37.5% correct. Top "defence" teams are minnows (Turks and Caicos, Brunei) — they concede rarely vs other minnows; model assigns them low δ and over-predicts their performance vs WC teams.

**Root cause**: Sparse training data (219 rows for 132 teams in 2010 fold) means per-team parameters have huge variance. The GLM's aggregate features (ELO, form) act as implicit regularisation; raw MLE with no shrinkage cannot generalise.

**Decision**: Abandon unregularised full DC MLE. Return to Poisson GLM as the base. Next: add more informative features or tune regularisation.

**Next step**: `/ds-feature-engineering` re-run to add squad strength (Transfermarkt), or `/ds-hpo` to tune GLM alpha.

---

## Experiment — 2026-06-14 (Experiment C)

**Hypothesis**: Pi-ratings (score-margin-aware, separate home/away ratings) contain information ELO discards — goal margin and directional home/away performance. Replacing ELO features with pi-ratings in the GLM should improve predictions, especially for teams whose form diverges from ELO's win/loss signal.

**Approaches tested**: Pi-Ratings GLM — penaltyblog `PiRatingSystem` computed from full match history (1990+) strictly temporally; replace `elo_home/away/diff` with `pi_home/away/diff`; all form features identical to GLM. LOTO-CV 4 folds × 64 matches.

**Result**: **4.375 pts/match [3.977, 4.781]** — +0.039 vs ELO GLM. 3 of 4 folds improve (2010: +0.125, 2014: +0.094, 2018: +0.235) but WC 2022 collapses to 3.469 (−0.297). Permutation test p=0.398. Pre-tournament sanity check on 2022 pi-ratings looks sensible (Brazil +3.66, Argentina +3.23). 2022 regression likely from tactical WC divergence from qualifying form.

**Decision**: Pi-ratings do not reliably beat ELO GLM. Pooled gain is marginal and not significant; 2022 regression is too large. ELO GLM remains safer for live WC 2026 predictions. Possible next step: hybrid GLM with both `elo_diff` AND `pi_diff` as features.

**Next step**: `/ds-experiment` — hybrid ELO+pi-ratings GLM (add `pi_diff` as extra feature alongside `elo_diff`); OR Experiment D (squad age feature from FIFA squad data); OR pivot to generating WC 2026 predictions with current best model (ELO GLM).

---

## Experiment — 2026-06-14 (Experiment B-fixed)

**Hypothesis**: Enforcing alpha ≥ 0.1 in Experiment B's inner CV grid will prevent the near-zero regularisation that caused the 2014 fold regression (−0.281).

**Approaches tested**: Same as Experiment B but `ALPHA_GRID = [0.1, 0.5, 1.0, 5.0, 10.0]`. All folds selected alpha=0.1.

**Result**: **4.344 pts/match [3.945, 4.750]** — fixed 2014 fold (+0.140, from 4.594→4.734) but cost signal in 2018 (−0.188, 4.750→4.562) and 2022 (−0.093, 3.859→3.766). Net: +0.008 vs GLM. The inner CV's low-alpha preference on large folds was capturing genuine per-team signal, not noise. No single alpha works across all fold sizes.

**Decision**: Team dummies are ruled out. No alpha value reliably improves all folds. Proceed to other approaches.

**Next step**: Experiment C (pi-ratings) — completed in same session.

---

## Experiment — 2026-06-14 (Experiment B)

**Hypothesis**: Adding one-hot team identity with L2 regularisation to the Poisson GLM will capture residual per-team signal beyond ELO + form, while preventing the overfitting that killed full DC MLE.

**Approaches tested**: Regularised GLM with `PoissonRegressor` + `OneHotEncoder` for home_team/away_team; inner 3-fold CV on training set to select alpha from [0.001, 0.01, 0.1, 1.0, 10.0] (scorer: neg_mean_poisson_deviance); LOTO-CV 4 folds × 64 matches.

**Result**: **4.379 pts/match [3.969, 4.781]** — +0.043 pts vs GLM baseline (4.336). Best in 3 of 4 folds. Large 2014 regression (−0.281, alpha=0.001) drags pooled mean. CI overlaps GLM — not statistically conclusive. Inner CV selects near-zero alpha on large folds (2014/2018/2022), allowing team-specific overfitting on training deviance that doesn't transfer to Sporza score.

**Decision**: Team dummies add marginal signal but regularisation strategy needs fixing. The inner CV metric (Poisson deviance) diverges from the objective (Sporza score) when data is abundant and alpha is very small. Options: (a) enforce alpha floor ≥ 0.1; (b) pivot to Experiment C (pi-ratings drop-in).

**Next step**: Experiment C — pi-ratings as ELO replacement in the plain GLM (1-hour drop-in); OR enforce alpha ≥ 0.1 and rerun Experiment B.

---

## Experiment — 2026-06-13 (run 3 — Experiment A)

**Hypothesis**: A Bayesian hierarchical Poisson model (Baio & Blangiardo 2010) with ELO-informed attack hyperpriors will regularise per-team parameters via shrinkage, fixing the overfitting that killed full DC MLE (3.762 pts) while retaining the team-level signal absent in the covariate-only GLM.

**Approaches tested**: Bayesian hierarchical Poisson (PyMC 6.0.1) — attack ~ Normal(ELO-scaled, sigma_attack), defence ~ Normal(0, sigma_defence); NUTS 1000 draws + 1000 tune, 2 chains; LOTO-CV 4 folds × 64 matches.

**Result**: **4.270 pts/match [3.887, 4.660]** — better than autofill (+0.13 pts) but **−0.066 pts below Poisson GLM (4.336)**. WC 2010 fold (most sparse): 4.391 pts — significantly better than DC MLE (2.922) confirming shrinkage fixed the overfitting. WC 2022 fold: 3.719 pts, below GLM's 3.766.

**Convergence**: Acceptable overall — max R̂ 1.025 on sparse 2010 fold (8 divergences), 1.010–1.015 on larger folds. ELO-informed sigma_attack increases with more data (0.13→0.32), reflecting more signal being released from prior. sigma_defence is larger (~0.65–0.73), indicating the defence surface has more variance than ELO captures.

**Root cause of underperformance vs GLM**: The Bayesian model replaces the covariate-based regression (ELO + form as direct inputs) with per-team parameters regularised toward ELO. But in sparse folds (219 rows / 133 teams), even hierarchical shrinkage leaves high posterior variance — and crucially, the model loses the `home_form_wr`, `home_form_gf`, `home_form_ga` features that carry recent form signal the GLM exploits directly. The GLM's covariate approach is a better regulariser when feature quality is high.

**Decision**: Poisson GLM remains the best model. Bayesian approach did NOT open the gap vs autofill beyond the GLM. Proceed to Experiment B (regularised GLM with team dummies) or Experiment C (pi-ratings) for further improvement.

**Next step**: Experiment B — regularised GLM with L2-penalised team dummies (`PoissonRegressor(alpha=...) + OneHotEncoder`). Or Experiment C — pi-ratings as ELO replacement in GLM.
