# Approach Shortlist — WK 2026 Match Score Prediction (Phase 2) — 2026-06-13

## Context

Current best model: Poisson GLM → **4.34 pts/match** [3.93–4.74]. Autofill baseline: **4.14 pts/match**. Gap is +0.20 pts; CI overlaps — not yet statistically significant. Two confirmed failure modes: (1) full per-team MLE overfits on sparse LOTO folds; (2) Dixon-Coles ρ correction is negligible. The goal is to open a wider, statistically significant gap vs autofill before the WC 2026 group stage ends.

Tournament constraint: Time is critical. Group stage is in progress. Experiments need to deliver WC 2026 predictions quickly.

---

## Ranked shortlist

| Rank | Approach | Why now | Expected gain | Implementation risk |
|------|----------|---------|---------------|---------------------|
| 1 | **Bayesian hierarchical Poisson with ELO hyperpriors** | Directly fixes the per-team overfitting that killed DC MLE; principled shrinkage; backed by Baio & Blangiardo 2010 | Moderate: likely +0.1–0.3 pts vs GLM if hyperpriors are well-specified | Medium: PyMC setup, MCMC ~5–10 min/fold; convergence not guaranteed |
| 2 | **Regularised GLM: add team dummies with L2 penalty** | Frequentist equivalent of Bayesian shrinkage; same fix, easier to tune; direct extension of working GLM | Moderate: similar to Bayesian approach if alpha is well-tuned | Low: sklearn PoissonRegressor(alpha=...) + cross-validate alpha; 2–4h |
| 3 | **Pi-ratings replacing or supplementing ELO diff** | Score-margin-aware rating; penaltyblog implements it; 1-hour experiment to test | Small: pi-ratings outperform ELO on domestic data (RPS 0.199 vs 0.204); international transfer unclear | Low: drop-in replacement for ELO diff in GLM |
| 4 | **Squad age feature (% players aged 27–31)** | Free feature from FIFA squad PDF already downloaded; WC winners cluster at this age range | Small: informative signal but likely dominated by ELO | Low: compute from squad PDF; add to GLM |
| 5 | **PELE-style market value adjustment (Transfermarkt with European bias correction)** | Silver Bulletin PELE applies ~30% haircut to non-UEFA teams; current model uses raw log market value | Small-medium: may improve calibration for CONCACAF/AFC teams where market values are artificially deflated | Low: apply multiplier to existing squad_values feature |
| 6 | **Gradient boosting (CatBoost/XGBoost) with Poisson objective** | Best-in-class on domestic datasets (RPS 0.1925, Yeung et al. 2024); strong non-linearity capture | Uncertain: domestic evidence doesn't transfer cleanly to 219-row LOTO folds; overfitting risk | Medium: implement + tune, but likely underperforms GLM on small data |
| 7 | **LLM enrichment (injury context, squad availability)** | Portfolio differentiator; fills structured data gaps | Negligible for exact score prediction | High for performance; low for portfolio |

---

## Specific next experiments recommended

### Experiment A (highest priority): Bayesian hierarchical Poisson with ELO informative priors

**Justification**: The core pain point is that per-team parameters overfit (DC MLE: 3.76 pts). The Bayesian hierarchical approach adds population-level hyperpriors that automatically regularise team parameters via shrinkage toward the group mean. Using ELO ratings as the mean of the attack/defence hyperprior distribution anchors the model to a validated strength signal. This is the principled solution to the sparsity problem.

**Implementation spec**:
```python
import pymc as pm

with pm.Model() as hierarchical_model:
    # Hyperpriors anchored to ELO
    mu_attack = pm.Normal("mu_attack", mu=elo_scaled, sigma=0.5)  # per-team ELO as prior mean
    sigma_attack = pm.HalfNormal("sigma_attack", sigma=0.3)
    
    attack = pm.Normal("attack", mu=mu_attack, sigma=sigma_attack, shape=n_teams)
    defence = pm.Normal("defence", mu=0, sigma=0.3, shape=n_teams)
    home_advantage = pm.Normal("home_advantage", mu=0.2, sigma=0.1)
    
    lambda_home = pm.math.exp(attack[home_idx] - defence[away_idx] + home_advantage)
    lambda_away = pm.math.exp(attack[away_idx] - defence[home_idx])
    
    goals_home = pm.Poisson("goals_home", mu=lambda_home, observed=y_home)
    goals_away = pm.Poisson("goals_away", mu=lambda_away, observed=y_away)
```

**LOTO-CV protocol**: Same 4-fold LOTO as existing experiments. Sample 2000 draws + 1000 tune per fold (~5–10 min on CPU). Log to MLflow. Compare mean Sporza pts.

**Literature basis**: Baio & Blangiardo (2010) — https://discovery.ucl.ac.uk/16040/; Sam Vaughan (2022 WC Bayesian model) — https://medium.com/@samvaughan01/world-cup-predictions-from-a-hierarchical-bayesian-model-537e2319cc5d

---

### Experiment B (fast, low risk): Regularised GLM with team dummies

**Justification**: The frequentist equivalent of Bayesian shrinkage. Add one-hot team dummies to the existing GLM (home_team_X, away_team_X), then add an L2 penalty. Cross-validate the penalty strength. This tests whether team-specific intercepts improve predictions when regularised — the intermediate step between the current covariate-only GLM and full Bayesian model.

**Implementation spec**:
```python
from sklearn.linear_model import PoissonRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# Add team dummy columns to feature matrix
# Grid search alpha in [0.001, 0.01, 0.1, 1.0, 10.0]
# Use nested LOTO-CV: inner loop for alpha, outer loop for Sporza score
model = PoissonRegressor(alpha=0.1, max_iter=1000)
```

**Expected outcome**: Either (a) regularised dummies improve → confirms per-team signal exists but needed shrinkage; or (b) no improvement → team-level residual is fully captured by ELO/form features already in model.

---

### Experiment C (drop-in, 1 hour): Pi-ratings as feature

**Justification**: Pi-ratings outperform ELO on domestic data (RPS 0.199 vs 0.204, penaltyblog). They encode score margin (goal difference) and separate home/away ratings — two pieces of information ELO discards. The penaltyblog library has a ready implementation.

**Implementation spec**:
```python
from penaltyblog.ratings import PiRatings
# Compute pi-ratings for each team at each match date
# Replace elo_home, elo_away with pi_home, pi_away in GLM feature matrix
# Keep all other features identical
# Run same LOTO-CV
```

**Risk**: Pi-ratings may underperform on international data where matches are infrequent (less data to learn from per team vs domestic weekly matches).

---

### Experiment D (free feature, 2 hours): Squad age enrichment

**Justification**: WC winning squads cluster around 26–29 average age. Feature is derivable from the official FIFA squad PDF already in the project. Low implementation cost, worth testing even if signal is small.

**Implementation spec**:
- Parse WC squad list (Wikipedia or existing `data/interim/wc2026_fixtures.parquet`)
- Compute: `pct_prime_age` = fraction of squad aged 27–31
- Compute: `mean_squad_age` = mean age across 26 players
- Add to GLM as additional features; check feature importance and LOTO-CV impact

---

### Experiment E (calibration, 1 hour): Transfermarkt European bias correction

**Justification**: PELE (Nate Silver) applies ~30% haircut to non-UEFA team market values to correct for Transfermarkt's European bias. The current GLM uses raw log market value. This may be causing the model to underestimate non-European teams' true quality.

**Implementation spec**:
- Apply multiplier: `adjusted_market_value = market_value * (1.0 if is_UEFA else 0.70)`
- Re-compute `log_squad_market_value_home/away` with adjusted values
- Run LOTO-CV; compare to current GLM
- Source of confederations: join team names to confederation from ELO data

---

## Assumptions and unknowns

- **Will Bayesian shrinkage actually help?** The theory says yes for sparse folds (219 training rows, 132 teams). But the Ribeiro et al. (2025) Brazilian Championship study found hierarchical and non-hierarchical performed similarly on 380 matches. At 219 rows the hierarchy advantage should be more pronounced — but not guaranteed.

- **Will per-team effects help at all?** The current GLM uses ELO, form, and market value as covariates — these already capture most of the team-specific signal. The question is whether residual team effects (beyond what ELO captures) are signal or noise in a sparse LOTO fold.

- **Does pi-ratings advantage transfer to international football?** Evidence is from domestic leagues (300k+ matches). International football has sparser match histories per team. The learning rate parameters for pi-ratings may need retuning for international data.

- **Market value staleness (906 days)**: Applying a European bias correction doesn't fix the fundamental staleness issue. A fresh Transfermarkt scrape or alternative (PELE uses own Transfermarkt API integration) would be needed for a material improvement.

- **WC 2026 is 48 teams (new format)**: The LOTO training data (WC 2006–2018) used 32-team format. The 2010 fold specifically (219 rows) will have even sparser coverage of smaller nations that are now included. Bayesian shrinkage is especially important for the 16 new entrant nations.

---

## Educational resources

- Baio & Blangiardo (2010) full paper: https://discovery.ucl.ac.uk/16040/1/16040.pdf
- Bayesian football prediction in Python (PyMC3 tutorial): https://pena.lt/y/2021/08/25/predicting-football-results-using-bayesian-statistics-with-python-and-pymc3/
- Pi-ratings explained (penaltyblog): https://pena.lt/y/2025/04/14/pi-ratings-the-smarter-way-to-rank-football-teams/
- PELE methodology (Nate Silver): https://www.natesilver.net/p/pele-methodology
- 2023 Soccer Prediction Challenge (CatBoost + pi-ratings SOTA): https://arxiv.org/html/2309.14807
- Open-source WC 2026 model (Elo + Dixon-Coles + Monte Carlo): https://github.com/Hicruben/world-cup-2026-prediction-model
- Extending Dixon-Coles (Michels, Ötting, Karlis 2023): https://arxiv.org/abs/2307.02139
- Handball WC 2019 underdispersed sparse count regression (relevant analogue): https://arxiv.org/pdf/1901.05722
- Calibration via betting odds (arXiv:1802.08848): https://arxiv.org/pdf/1802.08848

---

## Recommendation

**Primary recommendation: Experiment B first (regularised GLM with team dummies), then Experiment A (Bayesian hierarchical)**

**Why B before A:**
1. Experiment B is a 2–4 hour implementation with a clear interpretation: if L2-regularised team dummies improve the score, it confirms that per-team residuals are signal. This validates the motivation for Experiment A before investing in PyMC setup.
2. If regularised dummies do NOT help, the current covariate-only GLM is already extracting the available signal, and Experiment A is less likely to succeed.
3. If regularised dummies help significantly, they may themselves produce a publishable result without MCMC overhead.

**Why A is the theoretically strongest bet:**
The Bayesian hierarchical model with ELO hyperpriors is the only approach with (a) strong theoretical motivation for the sparse-data setting, (b) published validation on football data (Baio & Blangiardo 2010), and (c) a direct solution to the identified failure mode (full DC MLE overfitting). The hyperprior anchoring on ELO is the key innovation not present in standard Baio & Blangiardo.

**What not to do next:**
- Do not try bivariate Poisson — ρ correction already tested and found negligible; bivariate Poisson solves the same problem at higher cost.
- Do not try gradient boosting without first solving the regularisation problem — 219-row folds will overfit XGBoost even with aggressive hyperparameter tuning.
- Do not pursue LLM enrichment for score improvement — no evidence it beats the GLM on exact scores.

**Expected timeline**: Experiments B + C can be completed in one session (~4–6h). Experiment A (Bayesian) requires a clean afternoon (~6–8h for PyMC setup + debugging + 4-fold LOTO runs).
