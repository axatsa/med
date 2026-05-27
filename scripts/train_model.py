"""
Generate synthetic training data based on clinical thresholds and train XGBoost.
Run once: python scripts/train_model.py
Model saved to assets/pe_model.pkl
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from xgboost import XGBClassifier

SEED = 42
N = 2000  # synthetic samples
rng = np.random.default_rng(SEED)

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "pe_model.pkl")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)


def _gen_sample(high_risk: bool) -> list:
    """Generate one synthetic patient feature vector."""
    if high_risk:
        sflt1_ratio = rng.normal(55, 20)
        il6 = rng.normal(25, 12)
        il10 = rng.normal(4, 2)
        vegfa = rng.normal(80, 25)
        map_p = rng.normal(100, 8)
        prev_pe = rng.choice([0, 1], p=[0.4, 0.6])
        mcp1 = rng.normal(400, 100)
        ip10 = rng.normal(350, 80)
        tnf = rng.normal(25, 8)
        pn_degree = rng.choice([1, 2, 3], p=[0.15, 0.55, 0.30])
        pi = rng.normal(2.0, 0.4)
        fgr = rng.choice([0, 1], p=[0.3, 0.7])
        il6_gen = rng.choice([0, 1, 2], p=[0.1, 0.3, 0.6])   # GG dominant
        il10_gen = rng.choice([0, 1, 2], p=[0.1, 0.3, 0.6])  # AA dominant
        vegfa_gen = rng.choice([0, 1, 2], p=[0.5, 0.3, 0.2])
        chtn = rng.choice([0, 1], p=[0.4, 0.6])
        pigf = rng.normal(50, 20)
        sflt1 = sflt1_ratio * max(pigf, 10)
    else:
        sflt1_ratio = rng.normal(18, 8)
        il6 = rng.normal(2.5, 1.5)
        il10 = rng.normal(18, 6)
        vegfa = rng.normal(160, 30)
        map_p = rng.normal(78, 8)
        prev_pe = rng.choice([0, 1], p=[0.92, 0.08])
        mcp1 = rng.normal(150, 50)
        ip10 = rng.normal(100, 40)
        tnf = rng.normal(8, 3)
        pn_degree = rng.choice([1, 2, 3], p=[0.70, 0.25, 0.05])
        pi = rng.normal(1.1, 0.2)
        fgr = rng.choice([0, 1], p=[0.85, 0.15])
        il6_gen = rng.choice([0, 1, 2], p=[0.55, 0.35, 0.10])
        il10_gen = rng.choice([0, 1, 2], p=[0.55, 0.35, 0.10])
        vegfa_gen = rng.choice([0, 1, 2], p=[0.2, 0.4, 0.4])
        chtn = rng.choice([0, 1], p=[0.85, 0.15])
        pigf = rng.normal(120, 30)
        sflt1 = sflt1_ratio * max(pigf, 10)

    age = rng.normal(30, 6)
    bmi = rng.normal(27 if high_risk else 24, 4)
    ga = rng.normal(26 if high_risk else 32, 6)
    parity = rng.choice([0, 1, 2, 3], p=[0.4, 0.35, 0.15, 0.10])
    smoking = rng.choice([0, 1], p=[0.8, 0.2])
    dm = rng.choice([0, 1], p=[0.85 if not high_risk else 0.7, 0.15 if not high_risk else 0.3])
    anemia = rng.choice([0, 1], p=[0.7, 0.3])
    pn_dx = 1 if high_risk else rng.choice([0, 1], p=[0.4, 0.6])

    return [
        float(max(18, age)), float(max(15, bmi)), float(max(10, ga)), float(max(60, map_p)),
        float(parity), float(smoking), float(chtn), float(dm), float(anemia), float(prev_pe),
        float(max(0.1, il6)), float(max(0.5, il10)), float(max(10, mcp1)), float(max(10, ip10)),
        float(max(0.5, tnf)), float(max(10, vegfa)), float(max(5, pigf)), float(max(100, sflt1)),
        float(max(1, sflt1_ratio)), float(il6_gen), float(il10_gen), float(vegfa_gen),
        float(pn_dx), float(pn_degree), float(max(0.5, pi)), float(fgr),
    ]


def main():
    print("Generating synthetic data...")
    # 60% high-risk, 40% low-risk (reflects clinical referral population)
    n_high = int(N * 0.60)
    n_low = N - n_high

    X = [_gen_sample(True) for _ in range(n_high)] + [_gen_sample(False) for _ in range(n_low)]
    y = [1] * n_high + [0] * n_low

    X = np.array(X, dtype=np.float32)
    y = np.array(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=SEED, stratify=y)

    print(f"Training on {len(X_train)} samples, testing on {len(X_test)}...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=SEED,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    probs = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, probs)
    print(f"AUC on synthetic test set: {auc:.4f}")

    joblib.dump(model, OUT_PATH)
    print(f"Model saved → {OUT_PATH}")


if __name__ == "__main__":
    main()
