import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, roc_auc_score,
    confusion_matrix, accuracy_score
)
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE

# ── Feature columns ────────────────────────────────────────────────────────
FEATURE_COLS = [
    "age", "monthly_income", "employment_type",
    "upi_txn_per_month", "avg_txn_amount",
    "utility_bills_paid", "rent_payments_on_time",
    "mobile_recharge_regularity", "spending_variance",
    "income_stability_ratio", "savings_rate",
    "late_payments", "overdraft_count",
    "loan_amount_requested", "loan_tenure_months"
]

SCORE_MIN, SCORE_MAX = 300, 850  # CIBIL-like range

def load_and_preprocess(filepath="data/credit_data.csv"):
    df = pd.read_csv(filepath)
    le = LabelEncoder()
    df["employment_type"] = le.fit_transform(df["employment_type"])
    joblib.dump(le, "model/label_encoder.pkl")
    return df

def map_to_credit_score(proba: float) -> int:
    """Map repayment probability (0–1) to credit score (300–850)."""
    return int(SCORE_MIN + proba * (SCORE_MAX - SCORE_MIN))

def get_risk_tier(score: int) -> str:
    if score >= 750: return "Low Risk"
    elif score >= 650: return "Moderate Risk"
    elif score >= 550: return "High Risk"
    else: return "Very High Risk"

def train():
    os.makedirs("model", exist_ok=True)

    df = load_and_preprocess()

    X = df[FEATURE_COLS]
    y = df["repaid"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Handle class imbalance with SMOTE
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

    # XGBoost model
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42
    )

    model.fit(
        X_train_res, y_train_res,
        eval_set=[(X_test, y_test)],
        verbose=False
    )

    # Evaluation
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    auc = roc_auc_score(y_test, y_proba)
    acc = accuracy_score(y_test, y_pred)

    print("\n" + "="*50)
    print("       MODEL EVALUATION RESULTS")
    print("="*50)
    print(f"  Accuracy  : {acc:.4f}")
    print(f"  ROC-AUC   : {auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Defaulted", "Repaid"]))

    # Save model
    joblib.dump(model, "model/xgboost_model.pkl")
    print("✅ Model saved to model/xgboost_model.pkl")

    # SHAP explainer
    explainer = shap.TreeExplainer(model)
    joblib.dump(explainer, "model/shap_explainer.pkl")
    print("✅ SHAP explainer saved to model/shap_explainer.pkl")

    # Save feature names
    joblib.dump(FEATURE_COLS, "model/feature_cols.pkl")

    return model, auc, acc

if __name__ == "__main__":
    train()
