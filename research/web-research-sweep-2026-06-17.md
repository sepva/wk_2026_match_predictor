# Web Research Sweep — WC 2026 Exact Score Prediction (2026-06-17)

## Scope

Broad web sweep focused on empirical evidence for improving exact score prediction in international football/WC settings, with explicit attention to sparse-data robustness and calibration.

---

## 1) Best-performing model families in recent literature (2022–2025)

### Observed pattern

- In accessible WC-focused work, **hybrid systems** (goal models + exogenous priors/features + simulation) are the strongest practical approach.
- Peer-reviewed WC-specific comparisons in 2022–2025 often provide stage-dependent conclusions (group vs knockout) rather than one universal winner.
- Fully comparable exact-score benchmarks under custom scoring rules (like Sporza 10/7/5) remain scarce.

### Evidence

- **Zeileis et al. WC 2022 forecasting pipeline** blends:
  1. historical bivariate-Poisson ability modeling,
  2. bookmaker consensus,
  3. market/team/country covariates with random forest blending,
  4. large tournament simulation.  
  Source: https://www.zeileis.org/news/fifa2022/

- **Ribeiro et al. (2024) comparative international study** (WC 2022 + AFCON 2023): dynamic goal-based and ML approaches trade off by stage; no single method dominates all settings.  
  Source: https://arxiv.org/abs/2405.10247

- **Gilch (2022) nested ZIGP Poisson** reports improvements versus plain Poisson on historical tournament tests, but not uniformly across all tournaments.  
  Source: https://arxiv.org/abs/2205.04173

---

## 2) Novel feature engineering beyond simple Elo/form

### Betting odds as calibration signal

- Bookmaker market information is repeatedly used in high-performing tournament hybrid systems and is typically high value for probability calibration.
- Practical barrier: free historical WC odds coverage is limited; odds are easier to use for current/future calibration than broad historical backfills.

Sources:
- https://www.zeileis.org/news/fifa2022/
- https://www.zeileis.org/news/euro2024/
- https://arxiv.org/pdf/1802.08848

### xG and richer match-quality proxies

- Broad football evidence (league-heavy datasets) supports xG and rich contextual features for improving probabilistic metrics (log-loss/Brier).
- Transferability to sparse international/WC folds is plausible but not guaranteed.

Source:
- https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0282295

### Squad age/experience and market value adjustments

- Squad value, age composition, and structural context are used in recent hybrid pipelines.
- Strong practical signal exists; fully isolated WC-only effect sizes are still limited in public literature.

Sources:
- https://www.zeileis.org/news/fifa2022/
- https://www.natesilver.net/p/pele-methodology

### Confederation/context features

- Confederation-level context and tournament-stage effects are commonly cited as useful in international settings, particularly where strength calibration differs by region.
- Evidence is stronger as part of multifeature hybrids than as standalone effects.

---

## 3) Ensembles and stacking on sparse international data

### Main finding

- In open WC2026 implementations, **ensemble/calibrated approaches generally beat or match single Poisson components** on probabilistic metrics, with caveats on evaluation rigor.

### Open-source evidence

- **Hicruben/world-cup-2026-prediction-model**: walk-forward evaluation with RPS/log-loss/Brier/ECE reporting and explicit calibration diagnostics.  
  Source: https://github.com/Hicruben/world-cup-2026-prediction-model

- **eddiepiper/2026-world**: Elo + Poisson + XGBoost ensemble; reported holdout log-loss improvement over single components.  
  Source: https://github.com/eddiepiper/2026-world

- **pallab9999/fifa-worldcup-2026-prediction**: walk-forward WC backtests with multiple model families and stable mid-50% W/D/L accuracy range.  
  Source: https://github.com/pallab9999/fifa-worldcup-2026-prediction

### Reliability note

- These repos are valuable references, but mostly self-reported and not peer-reviewed; results should be treated as directional until reproduced in-project.

---

## 4) Rue & Salvesen dynamic attack/defence model

### What it is

- A dynamic extension of Poisson-type football models where latent team attack/defence strengths evolve over time (state-space style), instead of being static team effects.

### Practical evidence vs static GLM on WC data

- In the accessible 2022–2025 material, there is no clear, fully reported WC-specific benchmark showing consistent dominance over strong static/hybrid baselines.
- Closest evidence indicates stage-dependent wins and no universal leader in international tournament prediction.

Source:
- https://arxiv.org/abs/2405.10247

---

## 5) Era effects / score inflation and WC 2022 fold weakness

### Tournament goal-rate context

- 2014 WC: 171 goals / 64 matches = 2.67  
  Source: https://en.wikipedia.org/wiki/2014_FIFA_World_Cup
- 2018 WC: 169 / 64 = 2.64  
  Source: https://en.wikipedia.org/wiki/2018_FIFA_World_Cup
- 2022 WC: 172 / 64 = 2.69  
  Source: https://en.wikipedia.org/wiki/2022_FIFA_World_Cup

### Interpretation

- WC 2022 shows only a mild increase in average scoring vs 2014/2018, not a strong regime break.
- Persistent weakness on the WC 2022 fold is therefore unlikely to be explained by mean goal inflation alone; stronger candidates are calibration drift, feature non-stationarity, or matchup composition effects.

---

## 6) Open-source WC 2026 models worth studying

1. **Hicruben/world-cup-2026-prediction-model** — strongest calibration-first framing and metric discipline among discovered repos.  
   https://github.com/Hicruben/world-cup-2026-prediction-model
2. **pallab9999/fifa-worldcup-2026-prediction** — clean walk-forward setup and leak-aware discussion.  
   https://github.com/pallab9999/fifa-worldcup-2026-prediction
3. **eddiepiper/2026-world** — useful ensemble/reliability stack and operational framing.  
   https://github.com/eddiepiper/2026-world

---

## Compact source table

| Source | Year | Data/domain | Method | Metric signal reported | Confidence |
|---|---:|---|---|---|---|
| https://www.zeileis.org/news/fifa2022/ | 2022 | International/WC | Hybrid RF + ability + bookmaker + simulation | Strong practical hybrid design | Medium |
| https://arxiv.org/abs/2405.10247 | 2024 | WC 2022 + AFCON 2023 | Dynamic goal + ML comparison | Stage-dependent model performance | Medium |
| https://arxiv.org/abs/2205.04173 | 2022 | WC forecasting | Nested ZIGP Poisson | Better than plain Poisson in some tests | Medium |
| https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0282295 | 2023 | League football/xG | ML with richer feature set | Log-loss/Brier improvements | High |
| https://github.com/Hicruben/world-cup-2026-prediction-model | 2026 | International matches | Elo/DC/MC + calibration | Strong self-reported RPS/LL/Brier/ECE | Medium-Low |
| https://github.com/eddiepiper/2026-world | 2026 | International matches | Elo+Poisson+XGB ensemble | Ensemble LL gain (self-reported) | Low-Medium |
| https://github.com/pallab9999/fifa-worldcup-2026-prediction | 2026 | International+WC backtests | Elo/Poisson/XGB/MC | Mid-50% accuracy range | Low-Medium |
| https://en.wikipedia.org/wiki/2014_FIFA_World_Cup | 2014 | WC finals | Descriptive | 2.67 goals/match | Medium |
| https://en.wikipedia.org/wiki/2018_FIFA_World_Cup | 2018 | WC finals | Descriptive | 2.64 goals/match | Medium |
| https://en.wikipedia.org/wiki/2022_FIFA_World_Cup | 2022 | WC finals | Descriptive | 2.69 goals/match | Medium |

---

## Practical implications for next model iteration

1. Keep Poisson-GLM core but test **stacked calibration layer** (GLM + market/rating/exogenous blend).
2. Prioritize **calibration quality** (RPS/Brier/ECE) alongside Sporza points for sparse-fold stability.
3. Add/refresh exogenous features with highest practical value: **odds proxy**, **market-value correction**, **squad composition context**.
4. Treat claims from open repos as candidates to reproduce, not ground truth.
