"""
scikit-learn preprocessing Pipeline for the WK 2026 match predictor.

Separates features into numeric and categorical groups and applies
appropriate transformations. The pipeline is designed to slot directly
into a two-stage Pipeline(preprocessor, model).

Usage:
    from src.features.pipeline import build_pipeline, NUMERIC_FEATURES, CATEGORICAL_FEATURES
    from sklearn.linear_model import PoissonRegressor

    pipe = build_pipeline(PoissonRegressor())
    X_train = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_train = df["home_score"]
    pipe.fit(X_train, y_train)
"""

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.impute import SimpleImputer
import numpy as np

# Features always available (ELO covers all FIFA teams 2010+)
CORE_NUMERIC_FEATURES = [
    "elo_diff",
    "home_elo",
    "away_elo",
    "home_form_wr",
    "away_form_wr",
    "form_diff_wr",
    "home_form_gf",
    "away_form_gf",
    "form_diff_gf",
    "home_form_ga",
    "away_form_ga",
    "tournament_weight",
    "is_neutral",
]

# Squad value features — available for WC2026 teams but NaN for most historical matches.
# Imputed with median during preprocessing; use in WC2026 inference, optional in training.
SQUAD_VALUE_FEATURES = [
    "home_log_mv",
    "away_log_mv",
    "log_mv_diff",
]

NUMERIC_FEATURES = CORE_NUMERIC_FEATURES + SQUAD_VALUE_FEATURES
CATEGORICAL_FEATURES: list[str] = []  # no categorical features in Phase 1


def build_pipeline(model) -> Pipeline:
    """
    Return a fitted-ready sklearn Pipeline with ColumnTransformer preprocessing.

    Numeric pipeline:
      - median imputation (handles NaN squad values for non-WC2026 teams)
      - standard scaling

    Args:
        model: Any sklearn-compatible estimator (e.g. PoissonRegressor, XGBRegressor).

    Returns:
        sklearn.pipeline.Pipeline with steps [("preprocessor", ...), ("model", model)].
    """
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, NUMERIC_FEATURES),
        ],
        remainder="drop",
    )

    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", model),
    ])
