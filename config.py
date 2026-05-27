import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "pe-predictor-secret-2025")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'med.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_PATH = os.path.join(BASE_DIR, "assets", "pe_model.pkl")
    FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")
    MODEL_AUC = 0.89
    MODEL_LAST_UPDATED = "12.05.2025"
    MODEL_ALGORITHM = "Weighted Scoring + XGBoost Ensemble"
