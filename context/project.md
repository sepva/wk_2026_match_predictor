# Project: WK 2026 Match Predictor

## Project Summary

A machine learning system that predicts match outcomes for the 2026 FIFA World Cup, combining classical tabular ML with LLM-assisted feature enrichment or narrative generation. Built as a personal showcase of data science skills and to compete in the Sporza WK-pronostiek.

## Business Goal

Finish in the top 10 of a 100-person Sporza WK-pronostiek minicompetition by predicting exact match scores (home goals + away goals) for all 104 WK 2026 matches. Primary goal is portfolio value (end-to-end DS showcase); competition placement is the measurable proxy. Tournament has started (June 12, 2026) — using Sporza default picks until the model is ready; remaining group stage + knockout rounds are still predictable.

## Scoring System (Sporza — confirmed from wkpronostiek.sporza.be/rules)

**Group stage (per match, max 10 pts):**
- 10 pts — exact score (bullseye)
- 7 pts — wrong score, but correct goal difference (e.g. predict 3-1, result is 2-0)
- 5 pts — correct winner/draw, but wrong goal difference
- 1 pt — filled in any prediction (participation point)

**Knockout rounds (from round of 16, cumulative per match):**
- +10 pts — correct advancing team (counts even if decided by penalties)
- +6 pts — exact score after 90 or 120 min
- +4 pts — correct advancing team + correct goal difference bonus
- +1 pts - filled in any prediction (participation point)

**Implication for modeling:** exact score prediction is the highest-value target. Goal difference matters more than individual goal counts. The right formulation: predict (λ_home, λ_away) as Poisson rates → derive score distribution → submit score that maximises expected Sporza points. A pure win/draw/loss classifier leaves points on the table.

## Success Metrics

- Business metric: Top 10 finish in the 100-person minicompetition (current baseline: Sporza default / FIFA-ranking autofill)
- Technical proxy (group stage): Mean Sporza points per match on a held-out validation set of historical WC matches (max 10 pts/match); secondary — Brier score on win/draw/loss probabilities
- Baseline: Sporza "safe" autofill (FIFA-ranking-based) — correct result most of the time → ~5 pts/match average; rarely exact score
- Success threshold: Beat the FIFA-ranking autofill in mean pts/match on validation data (floor); aspirational — approach 7+ pts/match average (goal difference accuracy)

## Constraints

- Timeline: Tournament started June 12, 2026 — group stage in progress; predictions updateable until each match kicks off; model needed ASAP for remaining matches
- Budget/compute: Personal project; start local, scale to Azure as needed (cost-conscious)
- Compliance/privacy: No personal data; public datasets only; no proprietary data sources
- Operational: Predictions needed before each match day; low-latency serving not required; manual submission to Sporza UI acceptable

## Non-Goals

- Real-time data pipeline or fully automated submission (token refresh was explored and dropped as overkill — manual push via `scripts/push_sporza.py` is sufficient)
- Predicting results for already-played matches
- Optimizing for the full 200,000-participant global leaderboard (only the 100-person group matters)

## Data Sources

- Available now: None confirmed — EDA phase
- Planned: Historical international match results, FIFA world rankings, ELO ratings (club560/eloratings.net), tournament history, historical betting odds (as calibration reference)
- Optional enrichment: player stats (Transfermarkt, SofaScore), injury/squad availability data
- Risks: Data freshness for in-tournament squad state; coverage gaps for smaller nations; no guarantee of pre-match lineup data in time for submission

## ML Modality

Mixed tabular + LLM

- Core predictions: tabular ML (XGBoost / LightGBM / logistic regression) on structured match/team features
- LLM role: feature enrichment (e.g. summarizing team form narratives), explanation generation, or prompt-based calibration

## Target Stack

- Development: local Jupyter notebooks → `src/` Python package
- Experiment tracking: MLflow
- Data versioning: DVC with local remote (upgrade to Azure Blob when deploying)
- Deployment target: Azure ML Managed Endpoints or Azure AI Foundry (future)
- LLM: Azure AI Foundry (when LLM components are added)

## Team

- Seppe Vanswegenoven — Data Scientist (solo)

## AE Context

Personal side project — no billable AE engagement, no project code or Jira board.

## Supporting Artifacts

- context/input/ — place kickoff notes, raw data samples, reference papers, or competition rules here
