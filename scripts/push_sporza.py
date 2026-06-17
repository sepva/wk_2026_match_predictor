"""
Push predictions from a CSV file to the Sporza pronotool.

Usage:
  python scripts/push_sporza.py --predictions data/predictions/wc2026_predictions_20260614.csv
  python scripts/push_sporza.py --predictions data/predictions/wc2026_predictions_20260614.csv --dry-run

The bearer token is read from the SPORZA_TOKEN env var or --token argument.
Only future matches (AFTER_TODAY / NOT_STARTED) are pushed.
"""

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.sporza_client import (
    TEAM_NAME_MAP,
    fetch_matches,
    build_match_index,
    push_predictions,
    FUTURE_STATUSES,
)


def load_predictions(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"home_team", "away_team", "pred_home", "pred_away"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Predictions CSV missing columns: {missing}")
    return df


def map_to_sporza(df: pd.DataFrame, match_index: dict) -> list[dict]:
    """Match each prediction row to a Sporza matchId."""
    mapped = []
    unmatched = []

    for _, row in df.iterrows():
        home_nl = TEAM_NAME_MAP.get(row["home_team"])
        away_nl = TEAM_NAME_MAP.get(row["away_team"])

        if home_nl is None or away_nl is None:
            unmatched.append(f"  No NL name: {row['home_team']} vs {row['away_team']}")
            continue

        match = match_index.get((home_nl, away_nl))
        if match is None:
            unmatched.append(f"  No Sporza match: {home_nl} vs {away_nl}")
            continue

        if match["status"] not in FUTURE_STATUSES:
            # Skip already played matches silently
            continue

        mapped.append({
            "matchId": match["matchId"],
            "homeScore": row["pred_home"],
            "awayScore": row["pred_away"],
            "home_team": row["home_team"],
            "away_team": row["away_team"],
        })

    if unmatched:
        print(f"[warn] {len(unmatched)} predictions could not be matched:")
        for u in unmatched:
            print(u)

    return mapped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", required=True, help="Path to predictions CSV")
    parser.add_argument("--token", default=os.environ.get("SPORZA_TOKEN"), help="Bearer token")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be pushed, don't actually push")
    args = parser.parse_args()

    if not args.dry_run and not args.token:
        print("Error: SPORZA_TOKEN env var or --token required for live push")
        sys.exit(1)

    print("Fetching Sporza match list...")
    matches = fetch_matches(args.token)
    match_index = build_match_index(matches)
    future_count = sum(1 for m in matches if m["status"] in FUTURE_STATUSES)
    print(f"  {len(matches)} total matches, {future_count} future/upcoming")

    print(f"Loading predictions from {args.predictions}...")
    df = load_predictions(args.predictions)
    print(f"  {len(df)} prediction rows")

    predictions = map_to_sporza(df, match_index)
    print(f"  {len(predictions)} matched to future Sporza matches")

    if not predictions:
        print("Nothing to push.")
        return

    print("\nPredictions to push:")
    for p in predictions:
        print(f"  [{p['matchId']}] {p['home_team']} {p['homeScore']}-{p['awayScore']} {p['away_team']}")

    result = push_predictions(predictions, args.token or "", dry_run=args.dry_run)

    if not args.dry_run:
        success = result.get("success", [])
        print(f"\nPushed {len(success)} predictions successfully.")
        if len(success) != len(predictions):
            failed = set(p["matchId"] for p in predictions) - set(success)
            print(f"Failed matchIds: {failed}")


if __name__ == "__main__":
    main()
