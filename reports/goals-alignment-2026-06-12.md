# Goals Alignment — 2026-06-12

## Framing summary

- Goal: Finish top 10 in a 100-person Sporza WK-pronostiek minicompetition by predicting exact match scores for all 104 WK 2026 matches
- Decision impact: Each prediction is submitted to the Sporza platform before match kickoff; points accumulate across the tournament; can update predictions until each match starts
- Target user: Seppe (sole user); competition is the measurable outcome, portfolio showcase is the primary motivation

## Metrics and thresholds

- Business metric: Top 10 finish in the 100-person minicompetition
- Technical proxy: Mean Sporza points per match on held-out historical WC validation set (max 10 pts/match); Brier score on win/draw/loss as secondary signal
- Baseline: Sporza "safe" autofill (FIFA-ranking-based) — correct result most of the time → ~5 pts/match average; rarely exact score
- Success threshold: Beat ~5 pts/match baseline on validation data (floor); aspirational — approach 7+ pts/match (goal difference accuracy regularly)

## Scoring system implications

Actual Sporza scoring (confirmed from wkpronostiek.sporza.be/rules):
- 10 pts — exact score
- 7 pts — wrong score, correct goal difference (e.g. predict 3-1, result 2-0)
- 5 pts — correct winner/draw, wrong goal difference
- 1 pt — participation

**Key insight:** goal difference is the swing factor between 5 and 7 pts — it's more achievable than exact score but requires score regression, not just outcome classification. The scoring heavily penalises predicting the right winner with the wrong goal difference (5 vs 7 pts gap). The right technical formulation: predict (λ_home, λ_away) as Poisson rates → derive score distribution → submit the score that maximises expected Sporza points (not necessarily the mode score). Optimising log-loss on win/draw/loss alone leaves ~2 pts/match on the table.

## Constraints and non-goals

- Constraints: tournament started June 12, 2026; group stage predictions still updateable match-by-match; model must produce (home_goals, away_goals) point estimates or distributions
- Non-goals: real-time pipeline, automated submission, global leaderboard optimization, already-played matches

## Evidence from context/input/

- No artifacts in context/input/ yet — all answers from conversation; Sporza scoring rules confirmed via Toernooivoetbal.be
- Scoring system: assumption that Toernooivoetbal.be spelregels match Sporza exactly (confirmed consistent with 2022 edition; unverifiable directly due to JS-rendered Sporza site)

## Open questions

1. **Baseline exact score accuracy:** What % of WC matches historically end on the most-likely Poisson score? Needed to estimate realistic points ceiling. → Resolve in EDA.
2. **Betting odds as calibration:** Historical implied win probabilities from bookmakers are well-studied (~65–70% accuracy). Are historical odds data available for free? → Investigate in EDA/data sourcing.
3. **Tournament state:** Which group stage matches have already been played? What are the remaining predictable matches? → Need current WC 2026 fixture data.
4. **Sporza submission format:** Does the platform accept fractional predictions or only integer scores? → Check UI when submitting; assume integer scores for now.
5. **Knockout bracket dependencies:** Knockout predictions depend on group stage outcomes — need to handle uncertainty propagation for bracket prediction.
6. **Competition entrants:** How analytical are the other 99 participants? If mostly gut-pick casual, even a basic calibrated model may be sufficient for top 10.

## Feasibility gate

- ML necessary now: **Yes** — the scoring rule rewards calibrated score prediction, not just gut picks. A Poisson regression / Dixon-Coles model on historical match data is the established baseline and clearly outperforms FIFA-ranking heuristics on this scoring rule.
- Complexity check: A simple Poisson/Dixon-Coles model (no LLM, pure tabular) is likely sufficient to beat the gut-pick competition field and reach top 10. LLM enrichment is a portfolio differentiator, not a performance necessity. Start simple, add complexity only if validation results warrant it.
- Rules of ML applied:
  - Rule 1 (don't be afraid to launch without ML): A FIFA-ranking heuristic is the current fallback; it's already in use. ML is motivated by the scoring rule structure.
  - Rule 2 (instrument metrics first): Define validation set (historical WC matches) and mean-Sporza-pts metric before model selection.
  - Rule 3 (ML over complex heuristics): Once data is sourced, a trained Poisson model beats hand-tuned FIFA-ranking rules and is easier to update.
  - Rule 39 (launch decisions are proxies for long-term goals): Portfolio value > competition placement; don't over-optimize for the 100-person leaderboard at the expense of code quality and reproducibility.
