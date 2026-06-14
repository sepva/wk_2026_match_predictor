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

## Experiment — 2026-06-13 (run 3 — Experiment A)

**Hypothesis**: A Bayesian hierarchical Poisson model (Baio & Blangiardo 2010) with ELO-informed attack hyperpriors will regularise per-team parameters via shrinkage, fixing the overfitting that killed full DC MLE (3.762 pts) while retaining the team-level signal absent in the covariate-only GLM.

**Approaches tested**: Bayesian hierarchical Poisson (PyMC 6.0.1) — attack ~ Normal(ELO-scaled, sigma_attack), defence ~ Normal(0, sigma_defence); NUTS 1000 draws + 1000 tune, 2 chains; LOTO-CV 4 folds × 64 matches.

**Result**: **4.270 pts/match [3.887, 4.660]** — better than autofill (+0.13 pts) but **−0.066 pts below Poisson GLM (4.336)**. WC 2010 fold (most sparse): 4.391 pts — significantly better than DC MLE (2.922) confirming shrinkage fixed the overfitting. WC 2022 fold: 3.719 pts, below GLM's 3.766.

**Convergence**: Acceptable overall — max R̂ 1.025 on sparse 2010 fold (8 divergences), 1.010–1.015 on larger folds. ELO-informed sigma_attack increases with more data (0.13→0.32), reflecting more signal being released from prior. sigma_defence is larger (~0.65–0.73), indicating the defence surface has more variance than ELO captures.

**Root cause of underperformance vs GLM**: The Bayesian model replaces the covariate-based regression (ELO + form as direct inputs) with per-team parameters regularised toward ELO. But in sparse folds (219 rows / 133 teams), even hierarchical shrinkage leaves high posterior variance — and crucially, the model loses the `home_form_wr`, `home_form_gf`, `home_form_ga` features that carry recent form signal the GLM exploits directly. The GLM's covariate approach is a better regulariser when feature quality is high.

**Decision**: Poisson GLM remains the best model. Bayesian approach did NOT open the gap vs autofill beyond the GLM. Proceed to Experiment B (regularised GLM with team dummies) or Experiment C (pi-ratings) for further improvement.

**Next step**: Experiment B — regularised GLM with L2-penalised team dummies (`PoissonRegressor(alpha=...) + OneHotEncoder`). Or Experiment C — pi-ratings as ELO replacement in GLM.
