"""
Sporza pronotool API client.

Fetches match IDs from the Sporza API and pushes predictions.
Bearer token must be provided externally (expires after ~1h).
"""

import os
import requests
from typing import Optional

SPORZA_API = "https://api.sporza.be"
COMPETITION_ID = 8
FUTURE_STATUSES = {"AFTER_TODAY", "NOT_STARTED"}

# English name (as used in our predictions CSV) -> Dutch name (as used by Sporza)
TEAM_NAME_MAP = {
    "Algeria": "Algerije",
    "Argentina": "Argentinië",
    "Australia": "Australië",
    "Belgium": "België",
    "Bosnia & Herzegovina": "Bosnië en Herzegovina",
    "Brazil": "Brazilië",
    "Canada": "Canada",
    "Colombia": "Colombia",
    "Curaçao": "Curaçao",
    "DR Congo": "DR Congo",
    "Germany": "Duitsland",
    "Ecuador": "Ecuador",
    "Egypt": "Egypte",
    "England": "Engeland",
    "France": "Frankrijk",
    "Ghana": "Ghana",
    "Haiti": "Haïti",
    "Iraq": "Irak",
    "Iran": "Iran",
    "Ivory Coast": "Ivoorkust",
    "Japan": "Japan",
    "Jordan": "Jordanië",
    "Cape Verde": "Kaapverdië",
    "Croatia": "Kroatië",
    "Morocco": "Marokko",
    "Mexico": "Mexico",
    "Netherlands": "Nederland",
    "New Zealand": "Nieuw-Zeeland",
    "Norway": "Noorwegen",
    "Uzbekistan": "Oezbekistan",
    "Austria": "Oostenrijk",
    "Panama": "Panama",
    "Paraguay": "Paraguay",
    "Portugal": "Portugal",
    "Qatar": "Qatar",
    "Saudi Arabia": "Saudi-Arabië",
    "Scotland": "Schotland",
    "Senegal": "Senegal",
    "Spain": "Spanje",
    "Czech Republic": "Tsjechië",
    "Tunisia": "Tunesië",
    "Turkey": "Turkije",
    "Uruguay": "Uruguay",
    "USA": "Verenigde Staten",
    "South Africa": "Zuid-Afrika",
    "South Korea": "Zuid-Korea",
    "Sweden": "Zweden",
    "Switzerland": "Zwitserland",
}

_REVERSE_MAP = {v: k for k, v in TEAM_NAME_MAP.items()}


def _headers(token: str) -> dict:
    return {
        "accept": "*/*",
        "authorization": f"bearer {token}",
        "content-type": "application/json",
        "origin": "https://wkpronostiek.sporza.be",
        "referer": "https://wkpronostiek.sporza.be/",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
        ),
    }


def fetch_matches(token: Optional[str] = None) -> list[dict]:
    """Return all group-stage matches with their matchId, team names, and status."""
    url = f"{SPORZA_API}/spapp/1/matchdays/soccer/competition/{COMPETITION_ID}"
    headers = _headers(token) if token else {
        "accept": "*/*",
        "origin": "https://wkpronostiek.sporza.be",
        "referer": "https://wkpronostiek.sporza.be/",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
        ),
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    matchdays = resp.json()

    matches = []
    for md in matchdays:
        for m in md["matches"]:
            matches.append({
                "matchId": m["matchId"],
                "status": m["status"],
                "home_nl": m["homeTeam"]["name"],
                "away_nl": m["awayTeam"]["name"],
                "home_en": _REVERSE_MAP.get(m["homeTeam"]["name"]),
                "away_en": _REVERSE_MAP.get(m["awayTeam"]["name"]),
                "phase": md.get("phaseName", ""),
            })
    return matches


def build_match_index(matches: list[dict]) -> dict[tuple[str, str], dict]:
    """Build a lookup from (home_nl, away_nl) -> match record."""
    return {(m["home_nl"], m["away_nl"]): m for m in matches}


def push_predictions(predictions: list[dict], token: str, dry_run: bool = False) -> dict:
    """
    Push a list of predictions to Sporza.

    predictions: list of dicts with keys matchId, homeScore, awayScore.
    Returns the API response dict.
    """
    payload = [
        {
            "matchId": p["matchId"],
            "modifiedTime": None,
            "homeScore": int(p["homeScore"]),
            "awayScore": int(p["awayScore"]),
            "shootoutWinner": None,
            "points": None,
        }
        for p in predictions
    ]

    if dry_run:
        print(f"[dry-run] Would POST {len(payload)} predictions:")
        for p in payload:
            print(f"  matchId={p['matchId']} {p['homeScore']}-{p['awayScore']}")
        return {"dry_run": True, "count": len(payload)}

    url = f"{SPORZA_API}/pronotool/1/prono"
    resp = requests.post(url, json=payload, headers=_headers(token), timeout=10)
    resp.raise_for_status()
    return resp.json()
