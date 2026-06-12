# Data Quality Report — WK 2026 Match Predictor — 2026-06-12

## Summary

- **Overall status: WARN** (no hard blockers; team name harmonization is the main pre-engineering task)
- Checks run: 28
- Failed: 2 (ELO non-breaking spaces in team names; Moldova ELO rating=0)
- Warnings: 8 (inherited from EDA red flags; see details below)
- Deferred: 1 (SofIFA 5.2 GB file)

---

## 1. Completeness

### Mart Jürisoo results.csv (training backbone)

| Column | Null% | Status | Notes |
|--------|-------|--------|-------|
| date | 0% | ✅ | |
| home_team | 0% | ✅ | |
| away_team | 0% | ✅ | |
| home_score | 0.14% | ✅ | 70 future WC 2026 fixtures (not played yet) — expected |
| away_score | 0.14% | ✅ | Same 70 rows |
| tournament | 0% | ✅ | |
| city | 0% | ✅ | |
| country | 0% | ✅ | |
| neutral | 0% | ✅ | |

**Note:** The 70 "missing" scores are WC 2026 group stage fixtures (date range 2026-06-12 – 2026-06-27) not yet played. These are prediction targets, not data quality issues. Drop before training.

### ELO eloratings.csv

| Column | Null% | Status | Notes |
|--------|-------|--------|-------|
| date | 0% | ✅ | Stored as string (YYYY-MM-DD) — parse on load |
| team | 0% | ✅ | Non-breaking spaces (`\xa0`) in multi-word names — see Section 3 |
| rating | 0.46% | ⚠️ | 31 missing + 1 Moldova row with rating=0 (2025-12-13) |
| change | 0% | ✅ | |

### ELO elo_ratings_wc2026.csv

All 23 columns: 0% missing. ✅ 48 WC 2026 teams fully covered.

### Transfermarkt players.csv (squad-level enrichment)

| Column | Null% | Status | Notes |
|--------|-------|--------|-------|
| market_value_in_eur | 34% | ⚠️ | Per-team coverage varies widely (3%–92%); see Section 6 |
| current_national_team_id | 94.86% | ℹ️ | Expected — most players not in national squad; not a required column |
| international_caps / goals | 63% | ℹ️ | Not required for squad-level aggregation |
| agent_name | 46% | ℹ️ | Not used in model |
| contract_expiration_date | 34% | ℹ️ | Not used |
| height_in_cm / foot | 7–11% | ℹ️ | Not required for team-level aggregation |

### Transfermarkt player_valuations.csv

| Column | Null% | Status | Notes |
|--------|-------|--------|-------|
| player_club_domestic_competition_id | 4.45% | ✅ | Non-critical join key |

---

## 2. Schema

| Dataset | Column | Expected | Actual | Status |
|---------|--------|----------|--------|--------|
| MJ results.csv | date | datetime | datetime64 | ✅ |
| MJ results.csv | home_score | int/float | float64 | ✅ (NaN for future) |
| MJ results.csv | neutral | bool | bool | ✅ |
| ELO eloratings.csv | date | datetime | object (string) | ⚠️ Must parse on load |
| ELO eloratings.csv | team | str (clean) | str with `\xa0` | ❌ Normalize on load |
| ELO eloratings.csv | rating | float | float64 | ✅ |
| ELO eloratings.csv | change | int | int64 | ✅ |
| ELO WC2026 | All | — | All numeric/string | ✅ |
| Transfermarkt players | market_value_in_eur | float | float64 | ✅ |

---

## 3. Team Name Harmonization

This is the primary blocker for joining datasets. The canonical name set is the **Kaggle WC2026 `teams.csv` `team_name` column** (48 real teams). Below is the full lookup table mapping each source's variant to the canonical name.

### Canonical → variant mapping table

| Canonical (WC fixture) | ELO eloratings.csv | ELO WC2026 snapshot | Mart Jürisoo | Transfermarkt |
|---|---|---|---|---|
| USA | `United\xa0States` | United States | United States | United States |
| South Korea | `South\xa0Korea` | South Korea | South Korea | Korea, South |
| Ivory Coast | `Ivory\xa0Coast` | Ivory Coast | Ivory Coast | Cote d'Ivoire |
| Bosnia & Herzegovina | `Bosnia\xa0and\xa0Herzegovina` | Bosnia and Herzegovina | Bosnia and Herzegovina | Bosnia-Herzegovina |
| Czech Republic | `Czechia` | Czechia | Czech Republic | Czech Republic |
| DR Congo | `Democratic\xa0Republic\xa0of\xa0Congo` | DR Congo | DR Congo | DR Congo |
| Cape Verde | `Cape\xa0Verde` | Cape Verde | Cape Verde | Cape Verde |
| New Zealand | `New\xa0Zealand` | New Zealand | New Zealand | New Zealand |
| Saudi Arabia | `Saudi\xa0Arabia` | Saudi Arabia | Saudi Arabia | Saudi Arabia |
| South Africa | `South\xa0Africa` | South Africa | South Africa | South Africa |
| Curaçao | Curaçao | Curaçao | Curaçao | Curacao |
| Iran | Iran | Iran | Iran | Iran |

**Implementation note:** Apply `str.replace('\xa0', ' ')` to all ELO `team` column values on load. Use the lookup table above for joining.

### Fixture placeholder names (knockout rounds)

The OpenFootball WC 2026 JSON contains placeholder identifiers (`1A`, `W73`, `3A/B/C/D/F`, etc.) for unresolved knockout pairings. These are expected — do not harmonize or resolve until match pairings are known. Filter to `team not in placeholder_set` before joins.

---

## 4. Range and Row-level Checks

| Check | Dataset | Result | Status |
|-------|---------|--------|--------|
| Duplicate rows (date + home + away) | MJ results.csv | 2 duplicate pairs | ⚠️ |
| Negative home/away scores | MJ results.csv | 0 | ✅ |
| Future dates with scores | MJ results.csv | 0 | ✅ |
| Max score (31–0) | MJ results.csv | Legitimate (Aus vs Am.Samoa 2001) | ✅ |
| ELO rating = 0 | ELO eloratings.csv | 1 row: Moldova 2025-12-13 | ❌ Drop or impute |
| ELO rating range (0–2171) | ELO eloratings.csv | Valid range | ✅ |
| ELO change range (−86 to +86) | ELO eloratings.csv | Valid | ✅ |
| Duplicate (date + team) in ELO | ELO eloratings.csv | 0 | ✅ |

### Duplicate details (MJ results.csv)
1. Tahiti 2-1 New Caledonia AND Tahiti 1-2 New Caledonia on 1974-02-17 (Friendly) — likely home/away reversed; **keep lower-index row, drop second**.
2. Gibraltar 4-1 Cayman Islands on 2026-06-06 (two identical rows) — **drop second row as true duplicate**.

---

## 5. Distribution / Balance

This is a Poisson regression problem (goal counts), not classification. No class imbalance check required.

| Metric | Value | Status |
|--------|-------|--------|
| Mean home goals (all matches, 2010+) | 1.757 | ✅ Normal |
| Mean away goals (all matches, 2010+) | 1.182 | ✅ Normal |
| Draw rate | 22.7% | ✅ |
| WC-specific draw rate | 21.2% | ✅ |
| Goal distribution (visual Poisson fit) | Confirmed | ✅ |
| Market value distribution (TM) | Right-skewed | ℹ️ Log-transform before use |

---

## 6. Transfermarkt Coverage for WC 2026 Squads

| Team | TM name | Players | MV coverage |
|------|---------|---------|-------------|
| Saudi Arabia | Saudi Arabia | 498 | 3% ⚠️ |
| South Korea | Korea, South | 610 | 8% ⚠️ |
| Jordan | Jordan | 45 | 9% ⚠️ |
| Mexico | Mexico | 536 | 11% ⚠️ |
| Japan | Japan | 923 | 16% ⚠️ |
| Colombia | Colombia | 956 | 19% ⚠️ |
| Qatar | Qatar | 54 | 20% ⚠️ |
| New Zealand | New Zealand | 105 | 28% ⚠️ |
| Panama | Panama | 61 | 25% ⚠️ |
| Australia | Australia | 474 | 27% |
| Czech Republic | Czech Republic | 574 | 26% |
| Germany | Germany | 1,452 | 92% ✅ |
| Curaçao | Curacao | 77 | 92% ✅ |
| DR Congo | DR Congo | 152 | 91% ✅ |
| Spain | Spain | 2,169 | 90% ✅ |
| France | France | 1,890 | 87% ✅ |
| England | England | 1,682 | 87% ✅ |
| Netherlands | Netherlands | 1,555 | 87% ✅ |
| Portugal | Portugal | 1,261 | 88% ✅ |

**Recommendation:** Use squad-level aggregated market value (sum of top-N players by latest valuation) rather than mean, to reduce impact of 0-value players. For low-coverage nations, ELO is the reliable primary feature; market value is secondary enrichment only.

---

## 7. Data Freshness Audit

| Dataset | Last date | Staleness | Recommended use |
|---------|-----------|-----------|-----------------|
| ELO eloratings.csv | 2025-12-13 | 181 days | Training features (historical ELO at match date) |
| ELO elo_ratings_wc2026.csv | 2026-12-31 (snapshot) | 0 days | **WC 2026 pre-tournament team strength** — use this |
| FIFA rankings | 2024-06-20 | 722 days | Historical training only; NOT current strength |
| FiveThirtyEight SPI | 2023-06-04 | ~1095 days | Historical calibration reference only |
| Transfermarkt valuations | 2026-02-27 | ~105 days | Current squad value — acceptable freshness |

---

## 8. Bias Flags

No protected attributes (age, gender, race, name, postcode) in any feature set. The datasets are country-level aggregates — no individual-level protected attributes. No `/ds-fairness` follow-up required.

---

## 9. PataterieData Overlap Assessment

| | Count |
|--|-------|
| Matches in both Mart Jürisoo and PataterieData | 37,741 |
| Only in Mart Jürisoo | 11,734 |
| Only in PataterieData | 13,821 |

The 13,821 extra PataterieData matches are real (sample includes Brazil vs Spain 1986, etc.) — regional competitions, African/Asian qualifiers, and smaller tournaments not in Mart Jürisoo. 

**Decision:** Use Mart Jürisoo as the primary training source (higher curation quality). PataterieData extra matches are available for augmentation but require the same team name harmonization. Tournament coverage in PataterieData skews toward friendlies and minor cups — verify that adding them doesn't add noise before training.

---

## 10. Issues Resolution Summary

| Issue | Severity | Resolution |
|-------|----------|------------|
| ELO non-breaking spaces in team names | ❌ Blocker | `str.replace('\xa0', ' ')` on load |
| Moldova ELO rating = 0 (2025-12-13) | ❌ | Drop or impute from adjacent rows |
| 9 WC teams missing from ELO by name | ❌ Blocker | Use harmonization table (Section 3) |
| Transfermarkt name mismatches (5 teams) | ❌ Blocker | Use harmonization table (Section 3) |
| 2 duplicate rows in MJ results.csv | ⚠️ | Drop second row of each pair |
| 70 future fixture rows with null scores | ⚠️ | Drop before training; these are targets |
| FIFA rankings stale (722 days) | ⚠️ | Use for historical training features only |
| SPI discontinued | ⚠️ | Historical calibration reference only |
| Transfermarkt low MV coverage (SAU, KOR, JOR, MEX, JPN) | ⚠️ | Fall back to ELO for squad strength |
| PataterieData extra matches unverified | ℹ️ | Defer to feature engineering phase |
| SofIFA 5.2 GB player ratings file | ℹ️ | Deferred by user decision |

---

## Recommended next step

Data is clean enough for feature engineering. All blockers are pre-processing transforms, not data re-ingestion. Proceed to `/ds-feature-engineering` with this checklist:

1. On load: `elo['team'] = elo['team'].str.replace('\xa0', ' ')`
2. Drop Moldova ELO row with rating=0
3. Drop 2 duplicate rows from MJ results.csv (indices 9642, 49361)
4. Drop 70 null-score rows before training
5. Apply name harmonization table (Section 3) before any cross-dataset join
6. Use `elo_ratings_wc2026.csv` for WC 2026 pre-tournament team strength (not stale `eloratings.csv`)
7. Log-transform Transfermarkt market values
