# Method Survey — WK 2026 Match Score Prediction (Phase 2) — 2026-06-13

## Task

Predict (home_goals, away_goals) for FIFA World Cup 2026 matches to maximise expected Sporza points (10 pts exact score, 7 pts correct goal difference, 5 pts correct winner/draw), using a LOTO-CV over 4 historical WCs as the validation protocol.

## Framing assumptions

- Best model so far: Poisson GLM with ELO diff + 5-match rolling form + log squad market value + tournament weight + is_neutral → **4.34 pts/match** (autofill baseline: 4.14; CI overlaps)
- Full Dixon-Coles MLE (per-team αᵢ/δⱼ) overfit badly → 3.76 pts/match; root cause: sparse folds (219 training rows, 132 teams for 2010 fold)
- Dixon-Coles ρ correction on GLM lambdas: negligible improvement over GLM
- Target: open a statistically significant gap over autofill (4.14 pts/match)
- Primary constraint: small international dataset (~14k matches post-2010, ≤219 training rows per LOTO fold); any model must handle data sparsity
- No proprietary data; public datasets only; local compute first

---

## New data sources / features found

### 1. Pi-ratings as alternative team strength feature

- **Description**: Dynamic rating system by Constantinou & Fenton (2013) that measures teams in goal-difference units, with separate home/away ratings, score-margin awareness, and rapid form adaptation. Zero-centered: a +1.0 rating = 1 goal better than average opponent. Distinct from ELO (which ignores margin and draws).
- **Empirical evidence**: On Dutch Eredivisie 2023–24, pi-ratings achieve RPS 0.199 vs ELO 0.204 (lower is better); advanced Dixon-Coles/Poisson models reach 0.191–0.192. Constantinou & Fenton (2013) showed profitability vs bookmaker odds over 5 EPL seasons (2007/08–2011/12). In 2023 Soccer Prediction Challenge: CatBoost + pi-ratings achieved 55.82% accuracy and RPS 0.1925 — best result in the challenge.
- **Applicability to international football**: Pi-ratings require only goals + dates, same as ELO. For international football the key advantage is that score-margin encoding captures 3-0 vs 1-0 more accurately, potentially useful for strong national teams vs minnows.
- **Caveat**: The penaltyblog library implements pi-ratings; however, international football has sparser match histories than domestic leagues, so the learning rate may need tuning.
- **Confidence**: medium-high (domestic evidence strong; international transfer uncertain)
- **Sources**: https://pena.lt/y/2025/04/14/pi-ratings-the-smarter-way-to-rank-football-teams/ | http://www.constantinou.info/downloads/papers/pi-ratings.pdf

### 2. PELE-style: blend ELO with Transfermarkt market values and squad age

- **Description**: Nate Silver's PELE (Predictive Elo with Lineup Equilibria) extends ELO by blending in Transfermarkt squad market values and age-based mean reversion. It constructs algorithmic 23-player rosters (full credit to starting 11, partial to bench), applies a ~30% discount to correct for Transfermarkt's European bias, and uses age weighting (younger teams project to improve; older teams to decline). A "Tilt" dimension captures attacking vs defensive style from positional allocation.
- **Empirical evidence**: PELE is used for WC 2026 simulations (100k Monte Carlo runs); Spain 16% winner probability. No published accuracy comparison to raw ELO available, but Silver explicitly states that "some of the most predictive indicators don't derive from match results alone" for international football (where match frequency is low).
- **Actionable for this project**: The market value adjustment is the most directly replicable. The Transfermarkt data is already downloaded (906 days stale — freshness concern). Key insight: applying a ~30% squad value haircut to reduce European team inflation may improve calibration for non-UEFA teams. Age weighting (penalise squads outside 25–30 prime window) is a free feature derivable from the WC squad list already available.
- **Confidence**: medium (PELE methodology documented but no peer-reviewed accuracy benchmarks vs standard ELO published)
- **Sources**: https://www.natesilver.net/p/pele-methodology | https://www.natesilver.net/p/pele-international-football-rankings-soccer-ratings-projections

### 3. Squad average age as tournament performance feature

- **Description**: The last 10 WC-winning squads averaged 26.91 years old. Historical analysis shows the count of players aged 27–31 is a signal for tournament success (peak physical/technical combination). Outside this window (too young or too old) correlates with underperformance. Feature derivable from the official FIFA squad list PDF already downloaded.
- **Empirical evidence**: Narrative evidence: Germany WC 2014 squad averaged 27.6 years; champions cluster in 26–31 average age range. PMC study (Votteler & Höner, 2021) found peak individual soccer performance age ~27–28, varying by position.
- **Implementation cost**: Low. WC squad ages derivable from FIFA squad PDF + Wikipedia. Computable in <1 hour; add as a feature to the GLM.
- **Caveat**: This is a relatively weak signal for group stage (7-match tournament window). Signal noise is high. Useful as an additional feature but not a primary driver.
- **Confidence**: low-medium (narrative evidence strong; no causal ML benchmarks found for this specific feature)
- **Sources**: https://ilcuk.org.uk/what-wins-world-cups-youth-experience-or-money/ | https://pmc.ncbi.nlm.nih.gov/articles/PMC8182689/

### 4. Qualifier performance (recent competitive form)

- **Description**: WC qualifiers are the most recent high-stakes matches before the tournament. Goals scored/conceded during the qualification campaign (zone-specific: UEFA, CONMEBOL, AFC, CAF, CONCACAF, OFC) represent up-to-date competitive form. Currently, the 5-match rolling form uses all match types; splitting into qualifier-specific rolling form could isolate a cleaner signal.
- **Empirical evidence**: No specific paper found quantifying the incremental gain of qualifier-form vs all-match form. Practitioners (Hicruben WC 2026 open-source model) emphasise recency weighting as the primary lever, implicitly capturing qualifier form.
- **Implementation**: The Mart Jürisoo dataset already includes qualifier matches with `tournament` column — filter to `"FIFA World Cup qualification"` and compute a separate rolling feature.
- **Confidence**: low (no direct empirical comparison found; practitioner consensus only)
- **Sources**: https://github.com/Hicruben/world-cup-2026-prediction-model

### 5. Betting odds as features or calibration target

- **Description**: Bookmaker odds are systematically well-calibrated market-implied probabilities. Multiple papers show that integrating betting market odds into football prediction models reduces log-loss and improves probability calibration. A 2018 paper (arXiv:1802.08848) proposes combining historical match data and bookmaker odds in a single Poisson model, achieving lower log-loss than either source alone.
- **Empirical evidence**: Domain-driven probability identification paper (MDPI Mathematics 2025) found that integrating multiple betting market groups achieved "lowest log-loss and best probability calibration" vs models using only match data. For WC 2026, live odds are available from The Odds API (paid, ~$60/month) or can be scraped from free sites for historical matches.
- **Actionability for this project**: WC-specific historical odds are NOT freely available; the Kaggle datasets cover domestic leagues only. Short-term alternative: use odds as a Platt-scaling / isotonic regression calibration target post-hoc (calibrate predicted probabilities against historical match odds to reduce miscalibration on low-probability exact scores).
- **Confidence**: high (calibration value well-established); low for free WC-specific odds availability
- **Sources**: https://arxiv.org/pdf/1802.08848 | https://www.mdpi.com/2227-7390/13/24/3976

---

## Model improvements found

### 1. Bayesian hierarchical Poisson (Baio & Blangiardo 2010) — principled shrinkage

- **Description**: Hierarchical Bayesian model where each team's attack (αᵢ) and defence (δⱼ) parameters are drawn from population-level hyperpriors (typically Normal with μ_attack, μ_defence hyperparameters). Natural regularisation: teams with few matches are shrunk toward the population mean. The prior is the solution to the overfitting problem that broke full Dixon-Coles MLE on the sparse 2010 fold.
- **Empirical evidence**: Baio & Blangiardo (2010) validated on Italian Serie A 1991–92; the framework is now a standard reference in football analytics. A 2024 comparison study (Frontiers in Sports, Ribeiro et al.) compared hierarchical vs non-hierarchical Bayesian Poisson on the 2022 Brazilian Championship: de Finetti scores were similar (0.60–0.61), leading the authors to prefer non-hierarchical for simplicity — suggesting the benefit of hierarchy is most pronounced with truly sparse data (few matches per team), which is exactly the WC international case.
- **Compared to GLM baseline**: No direct head-to-head found on the exact international WC sparse-data setting. The key advantage is that hyperpriors automatically regularise team parameters — avoiding the divergence seen in full DC MLE on the 2010 fold (only 219 training rows, 132 teams).
- **ELO as informative prior**: The natural extension is to use ELO ratings as the μ hyperparameters (attack/defence prior means), anchoring team parameters to a known strength signal. This is well-supported in the literature.
- **Implementation complexity**: medium — requires PyMC (or Stan); sampling ~2–10 minutes per fold; MLflow-trackable
- **Confidence**: high (established method); medium (quantified improvement over GLM for international sparse data unclear)
- **Sources**: https://discovery.ucl.ac.uk/16040/ | https://pmc.ncbi.nlm.nih.gov/articles/PMC11949986/ | https://medium.com/@samvaughan01/world-cup-predictions-from-a-hierarchical-bayesian-model-537e2319cc5d

### 2. Regularised Poisson GLM with L2 (ridge) penalty on team parameters

- **Description**: Instead of full per-team MLE (which overfit), add an L2 penalty on the attack/defence parameters of the GLM. This is the frequentist equivalent of the Bayesian approach: shrinks team-specific effects toward zero (or toward ELO-predicted values). In statsmodels or sklearn, this is `PoissonRegressor(alpha=...)` or adding a regularisation term to the log-likelihood.
- **Empirical evidence**: NCBi/PMC review (Steyerberg et al., 2016) showed penalised regression outperforms MLE on sparse event data. The Handball WC 2019 paper (arXiv:1901.05722) specifically applied sparse count data regression to international tournament data with underdispersion — relevant analogue.
- **Compared to GLM baseline**: Regularised GLM should recover the current GLM performance while allowing more flexible per-team structure. The gain vs the current covariate-only GLM (no per-team dummies) is that it can capture systematic team residuals without overfitting.
- **Implementation complexity**: low — `sklearn.linear_model.PoissonRegressor(alpha=0.1)` or `statsmodels.api.GLM` with a custom penalised likelihood; no MCMC needed
- **Key experiment**: Add binary team dummy features (home_team_X, away_team_X) to current GLM + add L2 penalty; cross-validate alpha. This directly tests whether team-specific intercepts — when regularised — improve over the pure covariate approach.
- **Confidence**: medium-high (established in regression literature; football application is direct)
- **Sources**: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4982098/ | https://arxiv.org/pdf/1901.05722

### 3. Bivariate Poisson model

- **Description**: Models home and away goals jointly as a bivariate Poisson distribution with a correlation parameter λ₃. The correlation term allows positive covariance between goals (capturing "open game" vs "tight game" dynamics). Karlis & Ntzoufras (2003) is the canonical reference; a bivariate negative binomial variant gives slightly better RPS than independent Poisson.
- **Empirical evidence**: Karlis & Ntzoufras (2003) showed bivariate Poisson yields up to 14% more draw predictions than independent Poisson when λ₃ = 0.20. For RPS: bivariate negative binomial slightly outperforms independent Poisson, but "for weighted likelihood methods there was virtually no difference" (Oxford Academic JRSSSC 2025). Dixon-Coles ρ correction achieves the same goal (fixing low-score draw counts) more simply.
- **Compared to GLM baseline**: Marginal improvement. The ρ correction already tested in this project (4.328 vs 4.336) showed negligible gain. Bivariate Poisson would likely give a similarly small improvement at higher implementation cost.
- **Implementation complexity**: medium — not in standard libraries; requires custom MLE
- **Verdict**: Low priority given ρ correction already tested and found negligible. Skip unless bivariate Poisson is implemented as a single experiment day.
- **Confidence**: high (method is validated); low (meaningful improvement expected)
- **Sources**: http://www2.stat-athens.aueb.gr/~jbn/papers2/08_Karlis_Ntzoufras_2003_RSSD.pdf | https://academic.oup.com/jrsssc/article/74/3/717/7929974

### 4. CatBoost / XGBoost with team-strength features (pi-ratings + ELO)

- **Description**: Gradient-boosted tree model treating goals as a count (Poisson objective) or classifying on win/draw/loss, with team strength rating features (ELO, pi-ratings) as inputs. Bunker, Yeung et al. (2024) in the 2023 Soccer Prediction Challenge showed CatBoost + pi-ratings reached RPS 0.1925, best in the challenge, outperforming both deep learning and standard Poisson GLM variants.
- **Empirical evidence**: "CatBoost combined with pi-ratings achieved the best result of 0.1925 RPS and 55.82% accuracy, surpassing all 2017 Soccer Prediction Challenge entries" (arXiv:2309.14807, Yeung et al. 2024). The dataset was 300k+ domestic league matches — much richer than the WC international setting.
- **Compared to GLM baseline**: Outperforms Poisson GLM on large domestic-league datasets. The key caveat: this evidence is from 300k+ domestic matches. For WC international data with ~14k training rows and LOTO folds of 219 rows, gradient boosting is at severe risk of overfitting.
- **Key features identified as important**: Elo ratings by wide margin (100x more influential than next feature per Hicruben WC 2026 model). Goals scored/conceded, assists, ball possession also ranked high (Luo et al. 2025 MLP paper).
- **Implementation complexity**: medium — xgboost/catboost with Poisson objective; feature engineering needed
- **Confidence**: medium (domestic evidence strong; international/sparse-data transfer uncertain)
- **Sources**: https://arxiv.org/html/2309.14807 | https://link.springer.com/article/10.1007/s10994-024-06608-w

### 5. LLM-based prediction (GPT-4, Claude, multi-model ensemble)

- **Description**: LLMs predict match outcomes by transforming numerical features into contextual text prompts, then outputting probabilities or scores. A preprint (socarxiv:e5wpy) found LLMs "achieve comparable accuracy to traditional ML methods" for football prediction with "no model training required." A Euro 2024 POC (SoccerGPT, github.com/chrisby/SoccerGPT) used GPT-4o + Sportmonks API.
- **Empirical evidence**: "LLMs achieve comparable accuracy to traditional ML" — comparable means not better. No evidence of LLMs outperforming a well-tuned Poisson model on exact score prediction specifically. The "86.7% accuracy" claim in the MLP paper (Luo et al. 2025) is on win/draw/loss, not exact scores, and uses post-hoc statistical indicators (goals scored — which are known at match end, making it data leakage unless interpreted as prior tournament round features).
- **Compared to GLM baseline**: Not demonstrated to exceed a calibrated Poisson GLM for exact score prediction. Primary value is: (a) filling gaps where structured data is unavailable (injury context, squad morale), (b) portfolio demonstration.
- **Implementation complexity**: high (for performance gain); low (for qualitative enrichment)
- **Confidence**: low (for score prediction performance); medium (for portfolio value)
- **Sources**: https://osf.io/preprints/socarxiv/e5wpy_v1 | https://github.com/chrisby/SoccerGPT

### 6. Bayesian dynamic time-varying model (footBayes / arXiv:2508.05891)

- **Description**: Extension of Bayesian hierarchical model where team abilities are time-varying with spike-and-slab hyperpriors controlling how much each period's estimate borrows from previous periods. Implemented in the R package `footBayes`. Evaluated on 5 seasons of Bundesliga, EPL, La Liga. Achieves "better predictive performance than other discrete-time dynamic models."
- **Empirical evidence**: Paper (Macrì-Demartino, Egidi, Torelli 2025, arXiv:2508.05891) shows improvement over static Bayesian models on domestic league data. No international football evaluation found.
- **Compared to GLM baseline**: Likely better calibrated on clubs with seasonal form shifts; unclear benefit for WC prediction where matches are episodic (every 4 years) rather than weekly.
- **Implementation complexity**: high (R package; would need porting or R bridge); not recommended for immediate next experiment
- **Confidence**: medium (domestic evidence); low (international applicability)
- **Sources**: https://arxiv.org/abs/2508.05891

### 7. Nested Zero-Inflated Generalised Poisson (ZIGP) with per-team parameters

- **Description**: Gilch (2022, arXiv:2205.04173) proposes a ZIGP model for WC 2022 incorporating ELO + per-team attack/defence as covariates in a generalised Poisson with zero-inflation. Validated against previous tournaments and compared to other Poisson models.
- **Empirical evidence**: Abstract states validation against previous tournaments; no specific accuracy numbers extracted. Key contribution is zero-inflation correction (like ρ in Dixon-Coles but more parametric) + generalised Poisson (handles overdispersion). Uses data from 2016+ with time + relevance weighting.
- **Compared to GLM baseline**: Claims to outperform "other Poisson models" but metric is not specified in abstract.
- **Implementation complexity**: high (custom MLE); not directly available in standard libraries
- **Confidence**: low (no accessible accuracy numbers)
- **Sources**: https://arxiv.org/abs/2205.04173

### 8. Random forest hybrid with ability parameters (Groll et al. 2018)

- **Description**: Combines random forest with team ability parameters from ranking methods as additional covariates. Authors found "by combining the random forest with the team ability parameters from the ranking methods as an additional covariate we can improve the predictive power substantially." Applied to WC 2018. Three approaches: Poisson regression, random forest, ranking methods — hybrid outperformed individual approaches.
- **Empirical evidence**: Model slightly favoured Spain over Germany (Germany eliminated in group stage; arguably model failure). No specific accuracy metrics available from abstract.
- **Compared to GLM baseline**: Hybrid outperforms both standalone GLM and standalone random forest; the team-ability parameter is the key feature.
- **Insight for this project**: The most important single feature in all tree models is the team strength rating (ELO equivalent). This validates the current GLM's ELO-first approach. The tree layer mainly adds non-linear interactions at scale.
- **Confidence**: medium
- **Sources**: https://arxiv.org/abs/1806.03208

---

## SOTA in 2024–2026

### Best-performing method class for international exact score prediction

Based on research across leaderboards, arXiv papers, and practitioner implementations (2022–2026):

**For domestic league prediction (large data):** CatBoost + pi-ratings is the empirically strongest approach (arXiv:2309.14807, Yeung et al. 2024), achieving RPS 0.1925 on the 2023 Soccer Prediction Challenge. Deep learning (Inception + Transformer + MLP) achieves comparable but slightly worse RPS. This evidence is robust.

**For international WC prediction (sparse data):** No published benchmark comparison was found that directly measures Poisson GLM vs Bayesian hierarchical model on LOTO-CV of historical WCs. The practitioner consensus is:
- ELO difference remains the dominant feature by a large margin
- Bayesian hierarchical with ELO priors is the principled approach for sparse international data
- Full per-team MLE (Dixon-Coles) overfits on international data — confirmed by this project and consistent with what the handball WC paper (arXiv:1901.05722) found

**LLMs in 2024–2026:** Multiple LLM-based approaches (GPT-4o, Claude, multi-model ensembles) achieve accuracy "comparable to traditional ML" for win/draw/loss prediction. No evidence of LLMs outperforming a calibrated Poisson model for exact score prediction. The primary LLM use case is zero-shot prediction when structured data is unavailable — not a replacement for the GLM core.

**Trend:** The 2025–2026 SOTA for international tournament prediction (WC 2026) in open-source models uses Elo + Dixon-Coles bivariate Poisson + Monte Carlo simulation. The Hicruben WC 2026 open-source model (cup26matches.com) backtested 61% accuracy on three-way outcomes over 920 matches (Oct 2023–May 2026), Brier score 0.536 vs 0.667 for uniform prediction. It does not claim to beat betting markets.

### Pi-rating vs ELO for WC 2026 context

Pi-ratings (penaltyblog, Constantinou 2013) outperform ELO on domestic data (RPS 0.199 vs 0.204 on Eredivisie). For international football, the advantage may be smaller because score margins are already less meaningful (ELO's limitation is less severe when teams are farther apart in quality, which is common in WC qualifiers). Empirical test: replace ELO diff with pi-rating diff in current GLM — 1-hour experiment.

### Key finding: the GLM remains competitive

The Bayesian hierarchical model (with ELO hyperpriors) is the only method with a strong theoretical and empirical case for outperforming the current GLM specifically on the sparse international data problem. Gradient boosting methods are promising but risk overfitting given the small LOTO training sets. LLMs do not beat GLMs on exact score prediction.

---

## Conflicting evidence

- **Hierarchical vs non-hierarchical Bayesian Poisson**: Ribeiro et al. (Frontiers 2025) found similar performance between hierarchical and non-hierarchical on 380 Brazilian Championship matches (sufficient data). The hierarchical model's advantage should be most pronounced in the WC LOTO setting (219–287 training rows, 48–132 teams). The two findings are not contradictory — they apply to different data regimes.

- **Bivariate Poisson worth it?**: Karlis & Ntzoufras (2003) show 14% more draw predictions with bivariate Poisson (λ₃ = 0.20). But the Oxford Academic JRSSSC (2025) state "virtually no difference" between bivariate NB and independent Poisson for weighted likelihood methods. This project already tested Dixon-Coles ρ (which is the simpler equivalent) and found negligible gain (4.328 vs 4.336). Evidence points to bivariate correction being not worth the implementation cost.

- **Deep learning vs gradient boosting for football**: Yeung et al. (2024) arXiv:2309.14807 found CatBoost slightly outperforms Inception+Transformer+MLP (RPS 0.2085 vs 0.2098). Other papers claim neural network "86.7% accuracy" — this is win/draw/loss on 64 WC 2022 matches with post-hoc statistics (data leakage risk). The Springer paper (ML journal 2024) required authentication and was not accessible. Gradient boosting evidence on clean datasets is more reliable.

- **ELO vs FIFA ranking**: Multiple papers confirm ELO outperforms FIFA ranking points as a predictor. Bayesian BTD ranking (Macrì-Demartino et al. arXiv:2405.10247) "demonstrates overall better performance" in knockout stages vs both FIFA ranking and standard ELO. For this project, ELO is already the primary feature; BTD would require rebuilding the entire rating system.

---

## Leaderboards consulted

| Benchmark | URL | Top score | Notes |
|-----------|-----|-----------|-------|
| 2023 Soccer Prediction Challenge | https://arxiv.org/html/2309.14807 | RPS 0.1925 (CatBoost + pi-ratings) | 300k+ domestic matches; not international |
| 2017 Soccer Prediction Challenge (Berrar ratings) | https://arxiv.org/html/2309.14807 | 55.82% accuracy | Domestic leagues; international transfer uncertain |
| Hicruben WC 2026 backtest | https://dev.to/jerry_chen_dbaa6838e17336/ | 61% 3-way accuracy, Brier 0.536 | 920 international matches Oct 2023–May 2026 |
| PapersWithCode football | https://paperswithcode.com/ | No dedicated exact score leaderboard found | SoccerNet covers video, not tabular score prediction |

---

## Python libraries of note

| Library | Use | Status |
|---------|-----|--------|
| `penaltyblog` | Dixon-Coles, Bayesian models, pi-ratings, data scraping | Already referenced |
| `statsmodels` | Poisson GLM with regularisation options | In use |
| `pymc` | Bayesian hierarchical model | Not yet used |
| `catboost` / `xgboost` | Gradient boosting with Poisson objective | Not yet used |
| `footBayes` (R) | Bayesian dynamic time-varying model | R only; not recommended |
| `scipy.optimize` | MLE for custom regularised Dixon-Coles | In use (full DC MLE experiment) |
