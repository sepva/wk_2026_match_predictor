# Approach Shortlist — WK 2026 Match Score Prediction — 2026-06-12

## Ranked shortlist

| Rank | Approach | Why now | Trade-offs | Key risk |
|------|----------|---------|------------|----------|
| 1 | **Dixon-Coles Poisson + ELO features** | Established method for exact score prediction; `penaltyblog` library makes it 1-day work; directly optimizable for Sporza scoring | Doesn't capture modern tactical/player-level variation | ELO data availability/freshness for 2026 qualifiers |
| 2 | **Bayesian hierarchical model (Baio & Blangiardo)** | Better uncertainty quantification; natural handling of teams with few matches (shrinkage) | Slower to fit (MCMC); harder to iterate; overkill before baseline is validated | PyMC setup complexity; sampling time |
| 3 | **Poisson GLM (ELO diff only)** | Fastest to build (<1h); strong baseline; ELO difference alone is highly predictive | Ignores team-specific attack/defense asymmetry; less accurate on exact scores | May not beat Sporza autofill on exact score rate |
| 4 | **XGBoost/LightGBM on engineered features** | Can capture non-linear interactions; extensible with any feature | Needs large WC-specific training set to avoid overfit; feature engineering effort | WC data is sparse (≤22 tournaments); model may overfit |
| 5 | **LLM enrichment layer** | Portfolio differentiator; fills gaps for squad availability/injury context | No evidence it improves Poisson rates directly; adds latency + cost | Noise from hallucinated or stale LLM knowledge |

---

## Included baseline

- **Sporza FIFA-ranking autofill** — expected ~5 pts/match; correct result most of the time, rarely exact score. This is the floor to beat. Any model that doesn't clear this bar on the held-out WC validation set is not worth using.

---

## Recommended data acquisition order

**Phase 1 — Core (needed before any modeling)**

1. **Mart Jürisoo international results** (CC0, CSV) — core training data
   - https://github.com/martj42/international_results
   - Download: `results.csv`, `goalscorers.csv`, `shootouts.csv`

2. **World Football ELO Ratings** — primary team strength feature
   - Kaggle: https://www.kaggle.com/datasets/saifalnimri/international-football-elo-ratings
   - Or: https://www.kaggle.com/datasets/afonsofernandescruz/2026-fifa-world-cup-historical-elo-ratings (pre-built for 2026 teams)

3. **WC 2026 fixture list** — needed for submission targets
   - OpenFootball JSON: https://github.com/openfootball/worldcup.json
   - Or Kaggle: https://www.kaggle.com/datasets/areezvisram12/fifa-world-cup-2026-match-data-unofficial

**Phase 2 — Team-level enrichment (add when baseline is validated)**

4. **FIFA World Rankings (historical)** — secondary ELO complement
   - Kaggle: https://www.kaggle.com/datasets/cashncarry/fifaworldranking

5. **Transfermarkt market values** — squad talent-depth feature
   - Kaggle: https://www.kaggle.com/datasets/mexwell/football-data-from-transfermarkt
   - Tables needed: `players`, `player_valuations`, `national_teams`
   - Compute: top-18 player market values → squad total/median per national team

6. **EA Sports FC / FIFA player ratings (SofIFA)** — squad quality feature
   - Kaggle: search "EA FC 25 player ratings" or "FIFA 24 complete dataset"
   - Aggregate: position-weighted mean overall rating per squad (top-11 proxy)

7. **WC 2026 official squad lists** — maps players → national teams
   - Official FIFA PDF: https://fdp.fifa.org/assetspublic/ce281/pdf/SquadLists-English.pdf
   - Or Wikipedia: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_squads (scrapeable)
   - Needed to filter Transfermarkt/SofIFA to the actual 26-player WC squads

**Phase 3 — Tournament context + calibration**

8. **Fjelstul World Cup Database** — WC-specific context (stage, group, knockout history)
   - https://github.com/jfjelstul/worldcup

9. **FiveThirtyEight SPI archive** — calibration reference only, not training data
   - https://github.com/fivethirtyeight/data/tree/master/soccer-spi

---

## Recommended implementation sequence

### Phase 1 — Baseline (target: this week)
1. Download Mart Jürisoo results + ELO ratings
2. Build **Poisson GLM** with ELO difference + home/neutral flag → validate on held-out WC 2010–2022 matches
3. Compute mean Sporza pts/match on validation set; confirm it beats Sporza autofill baseline (~5 pts/match)

### Phase 2 — Dixon-Coles (target: week 2)
4. Extend to full **Dixon-Coles** with time decay + ρ correction using `penaltyblog`
5. Compare against Phase 1 GLM on same validation set
6. Add WC 2026 fixture list; generate first score predictions

### Phase 3 — Feature enrichment (target: if time permits)
7. Add recent form features (rolling 5-match window: goals, wins)
8. Optionally add XGBoost layer on top of Poisson rate predictions
9. LLM enrichment for squad availability if warranted

---

## Assumptions and unknowns

- **ELO freshness**: WC 2026 qualifiers ran through March 2026; the Kaggle ELO dataset must include qualifier results to reflect current team form. Verify update date before using.
- **Neutral venue**: WC 2026 is hosted by USA/Canada/Mexico — USA matches have a mild home advantage; all other matches are effectively neutral. The `neutral` flag in Mart Jürisoo handles this.
- **48-team format**: WC 2026 is the first 48-team tournament. Group stage has 3 teams per group → uneven match dynamics. This affects stage-based features.
- **Tournament filter for training**: Should you train on ALL international matches (friendlies included) or only competitive/WC matches? Friendlies are noisier. Dixon-Coles practitioners typically train on all but apply heavy time decay — test both.
- **Cold start for smaller nations**: Several WC 2026 qualifiers (e.g. first-time qualifiers from CONCACAF/CONMEBOL periphery) have sparse international records. Bayesian shrinkage handles this better than MLE Dixon-Coles.
- **Player ratings edition alignment**: EA FC 25 (2024 release) is the most current edition. For WC 2026, some players' ratings may be stale if no FC 26 dataset exists yet — verify which edition is current and whether FC 26 ratings are available on Kaggle.
- **Transfermarkt time-join**: Market values change frequently. Use the snapshot closest to tournament start (June 2026) — not the latest overall value, which may post-date the match.
- **Squad list filtering**: EA/SofIFA contains 17k+ players globally; you need only the ~1,248 in the WC 2026 squads. The FIFA squad list PDF is the authoritative filter — join on player name (fuzzy match needed for name variations).

---

## Educational resources

- https://dashee87.github.io/football/python/predicting-football-results-with-statistical-modelling-dixon-coles-and-time-weighting/ — Dixon-Coles with time weighting, Python implementation walkthrough
- https://penaltyblog.readthedocs.io/ — `penaltyblog` library docs; Dixon-Coles + Bayesian models
- https://pena.lt/y/2021/08/25/predicting-football-results-using-bayesian-statistics-with-python-and-pymc3/ — Bayesian football prediction with PyMC3
- https://artiebits.com/blog/predicting-football-results-with-statistical-modelling/ — Poisson GLM tutorial, good starting point
- https://arxiv.org/pdf/1806.01930 — ELO-based WC 2018 prediction paper; validates ELO over FIFA ranking

---

## Recommendation

**Primary recommendation: Dixon-Coles with ELO features (Rank 1)**

**Why**: It directly produces the Poisson rate output needed to maximize Sporza expected points (exact score + goal difference). `penaltyblog` wraps the implementation so it's buildable in a day. ELO is the best available off-the-shelf team strength signal. The validation strategy (held-out WC 2010–2022 matches) directly measures the business metric. This approach has the best ratio of implementation speed to expected performance improvement over the baseline.

Build the simpler Poisson GLM first (2 hours) as a sanity check, then extend to Dixon-Coles. Only add XGBoost or Bayesian layers if the Dixon-Coles validation result leaves meaningful room for improvement. LLM enrichment is a Phase 3 add-on for portfolio value, not a performance necessity.
