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
