import joblib
import numpy as np
import pandas as pd
import shap
from config import config

# ── Load artifacts once at import time ────────────────────────────────────
_model     = None
_explainer = None
_le        = None
_features  = None

def _load():
    global _model, _explainer, _le, _features
    if _model is None:
        _model     = joblib.load(config.MODEL_PATH)
        _explainer = joblib.load(config.EXPLAINER_PATH)
        _le        = joblib.load(config.ENCODER_PATH)
        _features  = joblib.load(config.FEATURES_PATH)

def _map_score(proba: float) -> int:
    return int(config.SCORE_MIN + proba * (config.SCORE_MAX - config.SCORE_MIN))

def _risk_tier(score: int):
    if score >= 750: return "Low Risk",      "#22c55e"
    if score >= 650: return "Moderate Risk", "#f59e0b"
    if score >= 550: return "High Risk",     "#ef4444"
    return "Very High Risk", "#7f1d1d"

def _eligibility(score: int):
    if score >= 700: return True,  "Eligible for loan"
    if score >= 550: return None,  "Requires manual review"
    return False, "Not eligible at this time"

def _preprocess(data: dict) -> pd.DataFrame:
    df = pd.DataFrame([data])
    df["employment_type"] = _le.transform([df["employment_type"].iloc[0]])
    return df[_features].astype(float)

def predict(data: dict) -> dict:
    """
    Run the full scoring pipeline.
    data must contain all keys in FEATURE_COLS (see train.py).
    Returns a result dict ready to be returned by the API.
    """
    _load()

    X    = _preprocess(data)
    proba= _model.predict_proba(X)[0][1]
    score= _map_score(proba)
    tier, color     = _risk_tier(score)
    eligible, msg   = _eligibility(score)

    # SHAP top 5
    shap_vals = _explainer.shap_values(X)[0]
    top = sorted(zip(_features, shap_vals), key=lambda x: abs(x[1]), reverse=True)[:5]
    top_factors = [
        {
            "feature":   name.replace("_", " ").title(),
            "impact":    round(float(val), 4),
            "direction": "positive" if val > 0 else "negative",
        }
        for name, val in top
    ]

    return {
        "credit_score":           score,
        "repayment_probability":  round(float(proba), 4),
        "risk_tier":              tier,
        "risk_color":             color,
        "eligible":               eligible,
        "eligibility_message":    msg,
        "top_factors":            top_factors,
    }
