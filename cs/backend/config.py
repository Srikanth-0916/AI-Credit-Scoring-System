import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY       = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG            = os.getenv("DEBUG", "True") == "True"
    PORT             = int(os.getenv("PORT", 5000))

    # Database
    DB_PATH          = os.getenv("DB_PATH", "credit_scoring.db")
    DATABASE_URL     = f"sqlite:///{DB_PATH}"

    # Model
    MODEL_DIR        = os.getenv("MODEL_DIR", os.path.join(os.path.dirname(__file__), "model"))
    MODEL_PATH       = os.path.join(MODEL_DIR, "xgboost_model.pkl")
    EXPLAINER_PATH   = os.path.join(MODEL_DIR, "shap_explainer.pkl")
    ENCODER_PATH     = os.path.join(MODEL_DIR, "label_encoder.pkl")
    FEATURES_PATH    = os.path.join(MODEL_DIR, "feature_cols.pkl")

    # Scoring
    SCORE_MIN        = 300
    SCORE_MAX        = 850
    CORS_ORIGINS     = os.getenv("CORS_ORIGINS", "*")

config = Config()
