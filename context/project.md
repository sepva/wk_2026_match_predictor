# Project: WK 2026 Match Predictor

## Project Summary

A machine learning system that predicts match outcomes for the 2026 FIFA World Cup, combining classical tabular ML with LLM-assisted feature enrichment or narrative generation. Built as a personal showcase of data science skills and to compete in the Sporza WK-pronostiek.

## Business Goal

Beat the Sporza WK-pronostiek competition by predicting match outcomes (win/draw/loss) more accurately than pure FIFA-ranking-based estimates. Secondary goal: demonstrate end-to-end data science skills from exploration to Azure deployment.

## Success Metrics

- Business metric: Finish higher in the Sporza WK-pronostiek than a naive FIFA-ranking baseline
- Technical proxy: Brier score / log loss on match outcome probabilities (win/draw/loss)
- Baseline: FIFA ranking-based probability assignment (higher-ranked team wins with fixed probability)
- Success threshold: Outperform random guessing; aspirational — approach betting odds accuracy

## Constraints

- Timeline: 2026 World Cup group stage starts June 2026 — model must be ready before tournament kick-off
- Budget/compute: Personal project; start local, scale to Azure as needed (cost-conscious)
- Compliance/privacy: No personal data; public datasets only; no proprietary data sources
- Operational: Predictions needed before each match day; low-latency serving not required

## Data Sources

- Available now: None confirmed — exploration phase
- Planned: Historical international match results, FIFA world rankings, player stats (transfermarkt, SofaScore, etc.), ELO ratings, tournament history, potentially historical betting odds
- Risks: Data quality and coverage for smaller nations; player availability / injury data freshness; no guarantee of pre-tournament squad data

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
