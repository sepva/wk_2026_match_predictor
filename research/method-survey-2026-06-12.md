# Method Survey — WK 2026 Match Score Prediction — 2026-06-12

## Task

Predict (home_goals, away_goals) for FIFA World Cup 2026 matches to maximise expected Sporza points (10 pts exact score, 7 pts correct goal difference, 5 pts correct winner/draw).

## Framing assumptions

- Target is exact score distribution, not just win/draw/loss
- Right output: Poisson rates (λ_home, λ_away) → score probability matrix → argmax expected Sporza points
- No real-time pipeline needed; predictions submitted manually before each match kicks off
- Primary training signal: historical international match results with team strength features
- No proprietary data; public datasets only

---

## Data Sources

### 1. Mart Jürisoo — International Football Results (PRIMARY)

- **URL**: https://github.com/martj42/international_results | https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017
- **Coverage**: 1872–2024, ~49,400 men's full internationals (excludes B-teams, U-23, Olympics)
- **Columns**: `date, home_team, away_team, home_score, away_score, tournament, city, country, neutral`
- **Bonus files**: `goalscorers.csv`, `shootouts.csv`
- **Format**: CSV
- **License**: CC0 (Public Domain)
- **Update frequency**: Regular contributor updates; GitHub repo takes PRs
- **Usefulness for Dixon-Coles**: ★★★★★ — exactly what you need; clean structure, long history, neutral flag
- **Confidence**: High

### 2. PataterieData — International Football Results (FRESHNESS SUPPLEMENT)

- **URL**: https://www.kaggle.com/datasets/patateriedata/all-international-football-results
- **Coverage**: 1872–present, ~50,000+ matches; **daily updates** during tournaments
- **Format**: CSV
- **License**: Unknown (check Kaggle page)
- **Usefulness**: Best source for matches played in 2025–2026, including WC qualifiers and recent friendlies
- **Confidence**: Medium (dataset quality not independently verified)

### 3. Fjelstul World Cup Database (TOURNAMENT CONTEXT)

- **URL**: https://github.com/jfjelstul/worldcup
- **Coverage**: 1930–2022 World Cups; 27 relational tables (matches, goals, bookings, substitutions, squads, referees)
- **Columns in matches table**: 38 columns including stage, group, venue, full-time score, half-time score, extra time, penalty shootout
- **Format**: CSV, JSON, SQLite, RData
- **License**: CC-BY-SA 4.0
- **Usefulness**: Rich tournament-level context; knockout stage dynamics; team-level WC history
- **Confidence**: High

### 4. OpenFootball World Cup (WC 2026 FIXTURES)

- **URL**: https://github.com/openfootball/worldcup | https://github.com/openfootball/worldcup.json
- **Coverage**: 1930–2026 including **WC 2026 fixture list**
- **Format**: Football.TXT (human-readable text) + JSON export
- **License**: Public Domain
- **Usefulness**: Only freely available source with WC 2026 fixture schedule (dates, groups, venues, team names)
- **Confidence**: Medium (community-maintained; verify completeness)

### 5. Schochastics Football Data (BROAD COVERAGE SUPPLEMENT)

- **URL**: https://github.com/schochastics/football-data
- **Coverage**: 1888–2023, 1.2M+ matches across 207 domestic leagues + 20 international tournaments
- **Format**: Parquet
- **License**: ODC-BY
- **Usefulness**: Cross-competition context; may help estimate attack/defense parameters for club-based features
- **Confidence**: High

### 6. FIFA World Rankings — Historical (TEAM STRENGTH FEATURE)

- **URL**: https://www.kaggle.com/datasets/cashncarry/fifaworldranking | https://www.kaggle.com/datasets/lucasyukioimafuko/fifa-mens-world-ranking
- **Coverage**: December 1992–present, monthly snapshots
- **Columns**: country, ranking, points, rank_change
- **Format**: CSV
- **License**: Check Kaggle page
- **Usefulness**: Off-the-shelf team strength feature; widely used in WC prediction models; but Elo outperforms FIFA points empirically
- **Confidence**: High

### 7. World Football ELO Ratings (TEAM STRENGTH FEATURE — PREFERRED)

- **URL**: https://eloratings.net | Kaggle: https://www.kaggle.com/datasets/saifalnimri/international-football-elo-ratings | https://www.kaggle.com/datasets/afonsofernandescruz/2026-fifa-world-cup-historical-elo-ratings
- **Coverage**: 1901–2026, all senior international teams
- **Format**: CSV (via Kaggle); web-only on eloratings.net (scrapeable)
- **License**: Kaggle datasets — check individual pages
- **Usefulness**: ★★★★★ — Elo outperforms FIFA rankings as a predictor (confirmed in multiple papers); time-decayed, zero-sum, methodologically sound
- **Note**: The "2026 FIFA World Cup Historical Elo Ratings" Kaggle dataset has pre-tournament Elo for all 48 qualified teams
- **Confidence**: High

### 8. FiveThirtyEight Soccer Power Index — SPI (HISTORICAL BASELINE REFERENCE)

- **URL**: https://github.com/fivethirtyeight/data/tree/master/soccer-spi
- **Files**: `spi_matches_intl.csv` (match-level with SPI ratings + forecasts), `spi_global_rankings_intl.csv`
- **Coverage**: 2016–2023 (no longer updated; FiveThirtyEight shut down SPI predictions in 2023)
- **Format**: CSV
- **License**: Open (FiveThirtyEight data terms)
- **Usefulness**: Useful as a calibration reference and validation baseline; shows what a professional model predicted
- **Confidence**: High

### 9. Historical Betting Odds

- **Kaggle — Beat The Bookie**: https://www.kaggle.com/datasets/austro/beat-the-bookie-worldwide-football-dataset — 500k+ matches, 11 years, 32 bookmakers, 1005 leagues
- **Kaggle — Historical Football Results + Betting Odds**: https://www.kaggle.com/datasets/mexwell/historical-football-resultsbetting-odds-data — 31 seasons
- **Coverage**: Primarily domestic leagues, not WC-specific
- **Usefulness**: Betting odds are a strong calibration signal (market-implied probabilities); can back-derive implied goal totals; not essential for core model but useful for calibration
- **Note**: No freely available WC-specific historical odds found. The Odds API (paid, ~$60–300/month) covers current WC 2026 odds.
- **Confidence**: Medium

### 10. WC 2026 Fixture + Results Data

- **Official**: https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures (web only, no download)
- **Kaggle (unofficial)**: https://www.kaggle.com/datasets/areezvisram12/fifa-world-cup-2026-match-data-unofficial
- **Kaggle (schedule)**: https://www.kaggle.com/datasets/rajeshsubramanian27/fifa26-schedule
- **GitHub API (no auth)**: https://github.com/rezarahiminia/worldcup2026 — free REST API, teams/groups/matches/standings/live scores
- **Format**: CSV / JSON
- **Usefulness**: Needed for submission — exact fixture IDs, dates, team names, and already-played results
- **Confidence**: Medium (unofficial datasets; cross-check with FIFA.com)

### 11. WC 2026 Official Squad Lists (26-player rosters)

- **Official FIFA PDF**: https://fdp.fifa.org/assetspublic/ce281/pdf/SquadLists-English.pdf — all 48 teams × 26 players; released June 1, 2026
- **Wikipedia**: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_squads — structured table per team; scrapeable
- **Columns**: jersey number, position (GK/DF/MF/FW), full name, DOB, caps, goals, current club
- **Coverage**: All 1,248 players in the tournament
- **Format**: PDF / HTML table
- **Usefulness**: Maps players → national teams; prerequisite for any player-level feature aggregation
- **Confidence**: High (official source)

### 12. EA Sports FC / FIFA Player Ratings (SofIFA)

- **URL**: https://www.kaggle.com (search "FIFA player ratings" or "EA FC 25 player ratings")
- **Source data**: sofifa.com — ~17,000–18,000 players per edition; FIFA 15 through EA FC 25/26
- **Columns (per player, ~89 total)**: overall rating, potential, position, nationality, club, age, pace, shooting, passing, dribbling, defending, physical + 30+ sub-attributes
- **Format**: CSV (multiple Kaggle datasets per edition)
- **License**: User-scraped from EA/SofIFA; generally open for research — check per-dataset terms
- **Usefulness for WC**: Squad quality proxy — aggregate per-position mean overall rating → team attack/defense quality feature. Literature (Yeung et al. 2023) shows ~2–5% improvement over ELO-only baseline.
- **Aggregation approach**: position-weighted mean overall (e.g. 40% defense, 30% midfield, 30% attack); or top-11/top-18 average as starting-lineup proxy
- **Key caveat**: EA ratings reflect EA's model, not objective ability — but they're widely validated as a proxy
- **Confidence**: High (535+ scholarly citations of SofIFA data)

### 13. Transfermarkt Player Market Values

- **Kaggle dataset**: https://www.kaggle.com/datasets/mexwell/football-data-from-transfermarkt — 12 tables, weekly updates
  - Relevant tables: `players` (name, nationality, market value, position), `player_valuations` (historical snapshots), `national_teams`
  - 30,000+ players, 400,000+ historical valuations
- **GitHub (ETL)**: https://github.com/dcaribou/transfermarkt-datasets — pre-built CSVs from the same scraper
- **License**: Scraped from Transfermarkt (grey area); Kaggle dataset is widely used for research
- **Usefulness**: Squad total/median/top-18 market value is a good talent-depth proxy; complements ELO (captures roster changes faster). Transfermarkt's own WC 2026 simulation (market value only) predicted France winner — but was imperfect for weaker nations.
- **Aggregation**: sum/mean of current market values for the 26-player squad; filter to starting-11 proxy for cleaner signal
- **Expected improvement**: ~2–5% over ELO-only baseline as an ensemble feature (practitioner estimates; no published WC-specific paper)
- **Confidence**: Medium-High

### 14. FBref — Player Performance Stats (xG, progressive actions)

- **URL**: https://fbref.com
- **Coverage**: International matches from ~2017+; WC 2022, Euro 2020/2024, Copa América, AFCON
- **Columns**: goals, assists, xG, npxG, progressive passes, progressive carries, key passes, defensive actions, pressures
- **Format**: HTML tables (web scrape required; no official download API)
- **License**: Public data; scraping is standard practice in football analytics community
- **Usefulness**: Most granular free player stats for international matches; useful for recent form features (last 2 tournaments per player). Historical depth limited pre-2017.
- **Limitation**: No automated download; requires scraping; international xG data less complete than club data
- **Confidence**: High (data quality); Medium (coverage completeness for all 48 nations)

### 15. StatsBomb Open Data (Event-Level)

- **URL**: https://github.com/statsbomb/open-data
- **Coverage for international football**: WC 2018 (partial), Women's WC — **very limited for men's international**
- **Format**: JSON (event-level: every pass, shot, carry, pressure with coordinates)
- **License**: CC-BY-4.0 (free for non-commercial research)
- **Usefulness**: Excellent granularity (xG with freeze frames, 360 data) but coverage gaps make it impractical as a primary feature source for WC 2026 prediction
- **Confidence**: High (data quality); Low (coverage for this use case)

### 16. WC 2026 Injury Tracker

- **ESPN**: https://www.espn.com/soccer/story/_/id/48572979/2026-fifa-world-cup-injuries-tracker-which-stars-miss-latest-info — updated throughout tournament
- **SofaScore / WhoScored**: Real-time injury/suspension status per player
- **Notable absences as of June 12, 2026**: Rodrygo (Brazil, ACL — ruled out), De Ligt (Netherlands, back surgery — unlikely)
- **Format**: Web only; no structured download
- **Usefulness**: Qualitative input for LLM enrichment layer; hard to encode systematically as a numeric feature
- **Confidence**: High (real-time); Low (structured data availability)

---

## Modeling Approaches

### 1. Dixon-Coles Poisson Model

- **Description**: Independent Poisson distributions for home and away goals, with team-specific attack/defense parameters and a low-score correction factor (ρ) for 0-0, 1-0, 0-1, 1-1. Time-decay weighting on training matches.
- **Empirical evidence**: Foundational paper (1997); still the standard baseline in football analytics. Outperforms simple Poisson on exact score prediction.
- **Narrative evidence**: Widely validated in practitioner blogs (dashee87, penaltyblog); direct implementation available in `penaltyblog` Python library.
- **Implementation complexity**: Low-Medium — `penaltyblog` wraps it; or ~100 lines with `scipy.optimize`
- **Data requirements**: Historical match results with scores + match dates (for time decay); team names for joining ratings
- **Compute/cost profile**: Fits in seconds on a laptop; no GPU needed
- **Azure deployment fit**: ✅ — trivial to run anywhere
- **Confidence**: High
- **Sources**: https://rss.onlinelibrary.wiley.com/doi/10.1111/1467-9876.00065 | https://dashee87.github.io/football/python/predicting-football-results-with-statistical-modelling-dixon-coles-and-time-weighting/ | https://penaltyblog.readthedocs.io/

### 2. Bayesian Hierarchical Model (Baio & Blangiardo)

- **Description**: Hierarchical Bayesian formulation where team attack/defense parameters are drawn from population-level hyperpriors. Naturally handles teams with few matches ("cold start") via shrinkage.
- **Empirical evidence**: Baio & Blangiardo (2010, Journal of Applied Statistics); validated on Italian Serie A + international tournaments.
- **Narrative evidence**: `penaltyblog` has a PyMC3 tutorial; often cited as the principled upgrade from Dixon-Coles.
- **Implementation complexity**: Medium — requires PyMC; longer sampling (~minutes per fit); harder to iterate quickly
- **Data requirements**: Same as Dixon-Coles + benefits from priors (e.g. Elo as informative prior)
- **Compute/cost profile**: CPU-bound MCMC; 1–5 minutes per fit locally
- **Azure deployment fit**: ✅ — MLflow-trackable; fits on standard compute
- **Confidence**: High
- **Sources**: https://discovery.ucl.ac.uk/16040/ | https://pena.lt/y/2021/08/25/predicting-football-results-using-bayesian-statistics-with-python-and-pymc3/

### 3. Poisson GLM with ELO Features

- **Description**: Simpler than Dixon-Coles — fit a Poisson GLM using `statsmodels` or `sklearn` with ELO difference, home advantage, and recent form as features. Predict λ directly from team-level covariates rather than fitting per-team parameters.
- **Empirical evidence**: Multiple WC prediction papers use this as a first model; accuracy ~62–75% on win/draw/loss
- **Narrative evidence**: Good first model; easy to extend; ELO difference alone is surprisingly predictive
- **Implementation complexity**: Low — <50 lines with statsmodels
- **Data requirements**: ELO ratings at match date, match results, home/neutral flag
- **Compute/cost profile**: Negligible
- **Azure deployment fit**: ✅
- **Confidence**: High
- **Sources**: https://artiebits.com/blog/predicting-football-results-with-statistical-modelling/ | https://arxiv.org/pdf/1806.01930

### 4. Gradient Boosting (XGBoost/LightGBM) on Engineered Features

- **Description**: Train XGBoost/LightGBM to predict goals separately for home and away. Features: Elo diff, FIFA ranking diff, recent form (last 5–10 matches), head-to-head record, tournament stage, days since last match, etc.
- **Empirical evidence**: WC 2018 random forest paper; WC 2022 Kaggle competition winners frequently used ensemble methods (~75% result accuracy on recent data).
- **Narrative evidence**: Higher expressiveness than GLM; but risks overfitting on limited WC data; better combined with GLM baseline
- **Implementation complexity**: Medium — feature engineering is the main effort
- **Data requirements**: All of the above + extensive feature engineering
- **Compute/cost profile**: Fast locally; MLflow experiment tracking recommended
- **Azure deployment fit**: ✅
- **Confidence**: Medium-High
- **Sources**: https://arxiv.org/pdf/1806.03208 | https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2024.1410632/full

### 5. LLM-Assisted Feature Enrichment (Portfolio Differentiator)

- **Description**: Use LLM (Azure AI Foundry) to generate qualitative team form summaries, injury impact scores, or motivation/pressure narratives. Encode as numeric features or use for post-hoc calibration.
- **Empirical evidence**: No direct evidence that LLM enrichment improves Poisson score prediction; but adds portfolio demonstration value.
- **Narrative evidence**: Useful for cases where structured data is missing (e.g., squad availability for smaller nations).
- **Implementation complexity**: Medium-High — requires prompting + structured output parsing
- **Data requirements**: Access to recent news/squad data; Azure AI Foundry endpoint
- **Compute/cost profile**: API calls per match day; cost-conscious usage needed
- **Azure deployment fit**: ✅ — designed for Azure AI Foundry
- **Confidence**: Low (on performance gains); High (on portfolio value)

---

## Key Features (by predictive importance, per literature)

| Rank | Feature | Data source | Notes |
|------|---------|-------------|-------|
| 1 | ELO rating difference | World Football ELO (Kaggle) | Outperforms FIFA ranking in multiple papers |
| 2 | Recent form: goals scored/conceded (rolling 5–10 matches) | Mart Jürisoo results | Practitioner consensus |
| 3 | Home/neutral advantage | Match `neutral` flag | ~+0.3 λ in Poisson terms; Dixon-Coles |
| 4 | Tournament stage (group vs knockout) | Fjelstul WC DB | Different dynamics; include as dummy |
| 5 | Time-decay weighting on training data | Match dates | Dixon-Coles; reduces stale match influence |
| 6 | Squad average EA/FIFA overall rating | SofIFA via Kaggle | Position-weighted mean; ~2–5% improvement over ELO-only |
| 7 | Squad total/top-18 market value | Transfermarkt via Kaggle | Talent-depth proxy; captures roster changes faster than ELO |
| 8 | Head-to-head historical record | Mart Jürisoo | Secondary; too few games per pairing |
| 9 | Player-level xG / progressive stats (recent tournaments) | FBref (scrape) | Useful for Phase 3 enrichment; limited free coverage pre-2017 |
| 10 | Injury/squad availability | ESPN tracker / SofaScore | Qualitative; best handled via LLM narrative feature |

**Player aggregation guidance** (from Yeung et al. 2023):
- Don't simply average all 26 squad ratings — use position-weighted aggregation
- Suggested weights: 35% defense (4 defenders), 35% midfield (4 midfielders), 30% attack (3 forwards)
- Use top-11 or top-18 as starting-lineup proxy rather than full-26 squad
- Market value: sum of top-18 player values gives a better signal than full-squad sum

---

## Conflicting evidence

- **ELO vs FIFA rankings**: ELO outperforms FIFA ranking points as a predictor in multiple studies (arxiv:1806.01930; Nate Silver's PELE). FIFA points are influenced by non-predictive factors (e.g. match importance weighting). Use ELO as the primary strength feature; include FIFA ranking as a secondary feature.
- **Training window length**: Dixon-Coles original paper uses all historical data with time decay. Some practitioners filter to last 3–5 years to avoid stale team identities. For WC 2026 with 48 teams, using more history (with heavy decay) is safer.
- **Low-score correction ρ**: Some extensions argue ρ is small in magnitude and not worth the extra complexity. Others (penaltyblog) argue it still improves exact score calibration. Include it for the score prediction use case.

---

## Candidate baseline

- **ELO-based Poisson GLM**: Fit a Poisson GLM with ELO difference + home advantage as the only features. Expected performance: ~5–6 pts/match (better than FIFA-ranking autofill, rarely nails exact scores). Trivial to implement. Serves as the reference floor for all other models.

---

## Leaderboards consulted

| Benchmark | URL | Notes |
|-----------|-----|-------|
| WC 2022 Kaggle competition | https://www.kaggle.com/datasets/shilongzhuang/soccer-world-cup-challenge | No single accuracy leaderboard; various notebooks report ~62–75% win/draw/loss accuracy |
| FiveThirtyEight SPI (WC 2022) | https://github.com/fivethirtyeight/data/tree/master/soccer-spi | Professional reference model; data archived |
| paperswithcode football | https://paperswithcode.com/ | No dedicated football score prediction benchmark found |

---

## Python libraries of note

| Library | Use |
|---------|-----|
| `penaltyblog` | Dixon-Coles, Poisson, Bayesian models; data scraping |
| `statsmodels` | Poisson GLM baseline |
| `pymc` | Bayesian hierarchical model |
| `scipy.optimize` | MLE fitting for Dixon-Coles |
| `lightgbm` / `xgboost` | Gradient boosting ensemble |
| `mlflow` | Experiment tracking |
