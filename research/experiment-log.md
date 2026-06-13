# Experiment Log

---

## Experiment — 2026-06-13

**Hypothesis**: A fitted Poisson model with ELO and form features will outperform both random guessing and a zero-parameter ELO-only predictor; even the simplest trained model should approach the Sporza autofill baseline (~5 pts/match).

**Approaches tested**: random Poisson marginal, ELO-only (zero params), Poisson GLM (ELO + form features)

**Result**: Poisson GLM wins on val (4.50 pts/match, 17.7% exact score). ELO-only more stable across val/test (3.73/4.27). None reach the 5.0 pt/match target. Autofill remains unbeaten.

**Decision**: Proceed to Dixon-Coles — the ρ low-score correction is the most likely single lever to close the gap, by improving draw probability and exact 1-0/0-1 accuracy.

**Next step**: `/ds-build` — implement Dixon-Coles with time decay using `penaltyblog`, evaluate on same val/test split.
