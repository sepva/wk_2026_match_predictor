"""Sporza WK-pronostiek scoring rules."""

from __future__ import annotations

import numpy as np
import pandas as pd


def sporza_points_group(pred_home: int, pred_away: int, actual_home: int, actual_away: int) -> int:
    """Compute Sporza group-stage points for a single match prediction."""
    if pred_home == actual_home and pred_away == actual_away:
        return 10  # exact score
    pred_diff = pred_home - pred_away
    actual_diff = actual_home - actual_away
    if pred_diff == actual_diff:
        return 7  # correct goal difference (wrong score)
    pred_result = int(np.sign(pred_diff))
    actual_result = int(np.sign(actual_diff))
    if pred_result == actual_result:
        return 5  # correct winner/draw
    return 1  # participation point


def sporza_points_series(
    pred_home: pd.Series,
    pred_away: pd.Series,
    actual_home: pd.Series,
    actual_away: pd.Series,
) -> pd.Series:
    """Vectorised Sporza group-stage points."""
    exact = (pred_home == actual_home) & (pred_away == actual_away)
    pred_diff = pred_home - pred_away
    actual_diff = actual_home - actual_away
    correct_gd = pred_diff == actual_diff
    correct_result = np.sign(pred_diff) == np.sign(actual_diff)

    pts = pd.Series(1, index=pred_home.index, dtype=int)
    pts[correct_result] = 5
    pts[correct_gd & ~exact] = 7
    pts[exact] = 10
    return pts


def mean_sporza_pts(
    pred_home: pd.Series,
    pred_away: pd.Series,
    actual_home: pd.Series,
    actual_away: pd.Series,
) -> float:
    return sporza_points_series(pred_home, pred_away, actual_home, actual_away).mean()


def score_breakdown(
    pred_home: pd.Series,
    pred_away: pd.Series,
    actual_home: pd.Series,
    actual_away: pd.Series,
) -> dict:
    """Return count breakdown by point category."""
    pts = sporza_points_series(pred_home, pred_away, actual_home, actual_away)
    total = len(pts)
    return {
        "n_matches": total,
        "exact_10": int((pts == 10).sum()),
        "goal_diff_7": int((pts == 7).sum()),
        "winner_5": int((pts == 5).sum()),
        "participation_1": int((pts == 1).sum()),
        "mean_pts": float(pts.mean()),
        "pct_exact": float((pts == 10).sum() / total),
        "pct_correct_result": float(((pts == 10) | (pts == 7) | (pts == 5)).sum() / total),
    }
