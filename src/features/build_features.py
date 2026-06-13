"""
Build match-level feature tables for training and WC 2026 prediction.

Entry points:
  build_training_features() -> pd.DataFrame   (historical matches 2010+)
  build_wc2026_features()   -> pd.DataFrame   (WC 2026 fixtures)

Both functions read directly from data/interim/ parquet files and
return a feature matrix ready for model training / inference.
"""

import pandas as pd
import numpy as np
from pathlib import Path

INTERIM_DIR = Path("data/interim")

# Tournament importance weights (1=friendly, 2=qualifier/nations league, 3=major tournament)
TOURNAMENT_WEIGHT = {
    "FIFA World Cup": 3,
    "UEFA Euro": 3,
    "Copa América": 3,
    "African Cup of Nations": 3,
    "AFC Asian Cup": 3,
    "FIFA World Cup qualification": 2,
    "UEFA Euro qualification": 2,
    "CONCACAF Nations League": 2,
    "UEFA Nations League": 2,
    "Gold Cup": 2,
    "CONCACAF Gold Cup": 2,
    "African Cup of Nations qualification": 2,
    "AFC Asian Cup qualification": 2,
    "Friendly": 1,
}

FORM_WINDOW = 5  # last N matches for rolling form features


def _load_interim():
    matches = pd.read_parquet(INTERIM_DIR / "matches.parquet")
    elo_history = pd.read_parquet(INTERIM_DIR / "elo_history.parquet")
    elo_wc2026 = pd.read_parquet(INTERIM_DIR / "elo_wc2026.parquet")
    squad_values = pd.read_parquet(INTERIM_DIR / "squad_values.parquet")
    wc2026_fixtures = pd.read_parquet(INTERIM_DIR / "wc2026_fixtures.parquet")
    return matches, elo_history, elo_wc2026, squad_values, wc2026_fixtures


def _add_elo_at_date(matches_df: pd.DataFrame, elo_df: pd.DataFrame) -> pd.DataFrame:
    """Add home_elo, away_elo, elo_diff using as-of join on date."""
    elo_by_date = elo_df.sort_values("date").reset_index(drop=True)
    m_sorted = matches_df.sort_values("date").reset_index(drop=True)

    home = pd.merge_asof(
        m_sorted[["date", "home_team"]].rename(columns={"home_team": "team"}),
        elo_by_date[["date", "team", "rating"]],
        on="date",
        by="team",
        direction="backward",
    ).rename(columns={"rating": "home_elo"})

    away = pd.merge_asof(
        m_sorted[["date", "away_team"]].rename(columns={"away_team": "team"}),
        elo_by_date[["date", "team", "rating"]],
        on="date",
        by="team",
        direction="backward",
    ).rename(columns={"rating": "away_elo"})

    m_sorted["home_elo"] = home["home_elo"].values
    m_sorted["away_elo"] = away["away_elo"].values
    m_sorted["elo_diff"] = m_sorted["home_elo"] - m_sorted["away_elo"]
    return m_sorted


def _build_team_view(matches_df: pd.DataFrame) -> pd.DataFrame:
    """Explode matches into one row per team per match for rolling form."""
    home = matches_df[["date", "home_team", "home_score", "away_score"]].copy()
    home.columns = ["date", "team", "goals_scored", "goals_conceded"]

    away = matches_df[["date", "away_team", "away_score", "home_score"]].copy()
    away.columns = ["date", "team", "goals_scored", "goals_conceded"]

    tv = pd.concat([home, away]).sort_values(["team", "date"]).reset_index(drop=True)
    tv["win"] = (tv.goals_scored > tv.goals_conceded).astype(float)
    return tv


def _add_rolling_form(matches_df: pd.DataFrame, team_view: pd.DataFrame, n: int = FORM_WINDOW) -> pd.DataFrame:
    """Add rolling form features (win rate, goals for/against per match)."""
    grp = team_view.groupby("team")
    team_view = team_view.copy()
    team_view["form_win_rate"] = grp["win"].transform(
        lambda x: x.shift(1).rolling(n, min_periods=1).mean()
    )
    team_view["form_gf"] = grp["goals_scored"].transform(
        lambda x: x.shift(1).rolling(n, min_periods=1).mean()
    )
    team_view["form_ga"] = grp["goals_conceded"].transform(
        lambda x: x.shift(1).rolling(n, min_periods=1).mean()
    )

    # deduplicate (same team can appear twice on same date if they played two matches)
    form = team_view.drop_duplicates(subset=["date", "team"], keep="last")[
        ["date", "team", "form_win_rate", "form_gf", "form_ga"]
    ]

    m = matches_df.merge(
        form.rename(columns={
            "team": "home_team",
            "form_win_rate": "home_form_wr",
            "form_gf": "home_form_gf",
            "form_ga": "home_form_ga",
        }),
        on=["date", "home_team"],
        how="left",
    )
    m = m.merge(
        form.rename(columns={
            "team": "away_team",
            "form_win_rate": "away_form_wr",
            "form_gf": "away_form_gf",
            "form_ga": "away_form_ga",
        }),
        on=["date", "away_team"],
        how="left",
    )
    m["form_diff_wr"] = m["home_form_wr"] - m["away_form_wr"]
    m["form_diff_gf"] = m["home_form_gf"] - m["away_form_gf"]
    return m


def _add_squad_value_features(matches_df: pd.DataFrame, squad_values: pd.DataFrame) -> pd.DataFrame:
    """Add log squad market value and diff (WC 2026 teams only; NaN for others)."""
    sv = squad_values[["team", "log_squad_mv_top23"]].copy()

    m = matches_df.merge(
        sv.rename(columns={"team": "home_team", "log_squad_mv_top23": "home_log_mv"}),
        on="home_team",
        how="left",
    )
    m = m.merge(
        sv.rename(columns={"team": "away_team", "log_squad_mv_top23": "away_log_mv"}),
        on="away_team",
        how="left",
    )
    m["log_mv_diff"] = m["home_log_mv"] - m["away_log_mv"]
    return m


def _add_tournament_context(matches_df: pd.DataFrame) -> pd.DataFrame:
    m = matches_df.copy()
    m["tournament_weight"] = m["tournament"].map(TOURNAMENT_WEIGHT).fillna(1.5)
    m["is_neutral"] = m["neutral"].astype(int)
    return m


FEATURE_COLS = [
    # Team strength
    "home_elo", "away_elo", "elo_diff",
    # Recent form
    "home_form_wr", "away_form_wr", "form_diff_wr",
    "home_form_gf", "away_form_gf", "form_diff_gf",
    "home_form_ga", "away_form_ga",
    # Squad quality (Transfermarkt, available for WC2026 teams)
    "home_log_mv", "away_log_mv", "log_mv_diff",
    # Match context
    "tournament_weight", "is_neutral",
]

TARGET_COLS = ["home_score", "away_score"]
META_COLS = ["date", "home_team", "away_team", "tournament"]


def build_training_features(
    start_date: str = "2010-01-01",
    require_elo: bool = True,
) -> pd.DataFrame:
    """
    Build match-level feature table for model training.

    Filters to matches from `start_date` onward. When `require_elo=True`,
    drops rows where either team is absent from ELO history (non-FIFA teams).

    Returns a DataFrame with META_COLS + FEATURE_COLS + TARGET_COLS.
    """
    matches, elo_history, _, squad_values, _ = _load_interim()

    elo_teams = set(elo_history.team.unique())

    m = matches[matches.date >= start_date].copy()

    if require_elo:
        m = m[m.home_team.isin(elo_teams) & m.away_team.isin(elo_teams)].copy()

    m = m.sort_values("date").reset_index(drop=True)

    # ELO at match date
    m = _add_elo_at_date(m, elo_history)

    # Rolling form (computed over all matches in the window, including those before start_date)
    all_matches_elo = matches[
        matches.home_team.isin(elo_teams) & matches.away_team.isin(elo_teams)
    ].sort_values("date").reset_index(drop=True)
    team_view = _build_team_view(all_matches_elo)
    # Keep only the subset we need for the join
    m = _add_rolling_form(m, team_view[team_view.date >= start_date])

    # Squad values (WC2026 squads only; NaN for most historical matches)
    m = _add_squad_value_features(m, squad_values)

    # Tournament context
    m = _add_tournament_context(m)

    # Final column selection
    available_targets = [c for c in TARGET_COLS if c in m.columns]
    return m[META_COLS + FEATURE_COLS + available_targets].copy()


def build_wc2026_features() -> pd.DataFrame:
    """
    Build feature table for WC 2026 fixture predictions.

    Uses WC 2026 ELO snapshot for team strength (fresher than historical ELO).
    Form features are computed from the full historical match record up to each fixture date.
    Squad market values are the February 2026 Transfermarkt snapshot.

    Returns a DataFrame with META_COLS + FEATURE_COLS (no targets for unplayed matches).
    Played matches include home_score / away_score if available.
    """
    matches, elo_history, elo_wc2026, squad_values, wc2026_fixtures = _load_interim()

    elo_teams = set(elo_history.team.unique())

    # Filter to fixtures with known team names (exclude knockout placeholders)
    is_placeholder = wc2026_fixtures.home_team.str.match(r"^[0-9WL]") | \
                     wc2026_fixtures.away_team.str.match(r"^[0-9WL]")
    fixtures = wc2026_fixtures[~is_placeholder].copy()
    fixtures = fixtures.rename(columns={"round": "tournament"})
    fixtures["neutral"] = True  # all WC 2026 matches are at neutral venues

    # ELO from WC2026 snapshot (single pre-tournament rating per team)
    elo_snap = elo_wc2026[["team", "rating"]].copy()
    fixtures = fixtures.merge(
        elo_snap.rename(columns={"team": "home_team", "rating": "home_elo"}),
        on="home_team", how="left"
    )
    fixtures = fixtures.merge(
        elo_snap.rename(columns={"team": "away_team", "rating": "away_elo"}),
        on="away_team", how="left"
    )
    fixtures["elo_diff"] = fixtures["home_elo"] - fixtures["away_elo"]

    # Form: rolling over all historical matches before each fixture date
    all_matches_elo = matches[
        matches.home_team.isin(elo_teams) & matches.away_team.isin(elo_teams)
    ].sort_values("date").reset_index(drop=True)
    team_view_full = _build_team_view(all_matches_elo)

    # Compute form state as of max(historical date) for each WC team
    # (fixture dates are in June 2026; historical data ends June 2026-06-11)
    grp = team_view_full.groupby("team")
    team_view_full = team_view_full.copy()
    team_view_full["form_win_rate"] = grp["win"].transform(
        lambda x: x.shift(1).rolling(FORM_WINDOW, min_periods=1).mean()
    )
    team_view_full["form_gf"] = grp["goals_scored"].transform(
        lambda x: x.shift(1).rolling(FORM_WINDOW, min_periods=1).mean()
    )
    team_view_full["form_ga"] = grp["goals_conceded"].transform(
        lambda x: x.shift(1).rolling(FORM_WINDOW, min_periods=1).mean()
    )

    # Take the last form snapshot per team (latest entry before first fixture)
    latest_form = (
        team_view_full.sort_values(["team", "date"])
        .groupby("team")
        .last()
        .reset_index()[["team", "form_win_rate", "form_gf", "form_ga"]]
    )

    fixtures = fixtures.merge(
        latest_form.rename(columns={"team": "home_team", "form_win_rate": "home_form_wr",
                                    "form_gf": "home_form_gf", "form_ga": "home_form_ga"}),
        on="home_team", how="left"
    )
    fixtures = fixtures.merge(
        latest_form.rename(columns={"team": "away_team", "form_win_rate": "away_form_wr",
                                    "form_gf": "away_form_gf", "form_ga": "away_form_ga"}),
        on="away_team", how="left"
    )
    fixtures["form_diff_wr"] = fixtures["home_form_wr"] - fixtures["away_form_wr"]
    fixtures["form_diff_gf"] = fixtures["home_form_gf"] - fixtures["away_form_gf"]

    # Squad market values
    fixtures = _add_squad_value_features(fixtures, squad_values)

    # Tournament context
    fixtures["tournament_weight"] = 3.0  # all WC matches weight 3
    fixtures["is_neutral"] = 1

    # Include scores for already-played matches
    available_targets = [c for c in TARGET_COLS if c in fixtures.columns]
    base_cols = META_COLS + FEATURE_COLS + available_targets
    extra = ["group", "venue", "played"]
    return fixtures[[c for c in base_cols + extra if c in fixtures.columns]].copy()
