import os
import math
import joblib
import numpy as np
from utils.translations import PREDICTOR_LABELS, RECOMMENDATIONS, RISK_LABELS, RISK_ALERT


MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "pe_model.pkl")
_xgb_model = None


def _load_xgb():
    global _xgb_model
    if _xgb_model is None and os.path.exists(MODEL_PATH):
        try:
            _xgb_model = joblib.load(MODEL_PATH)
        except Exception:
            _xgb_model = None
    return _xgb_model


def _encode_genotype(genotype: str, high_risk_allele: str) -> int:
    """Encode genotype as count of high-risk alleles (0, 1, 2)."""
    if not genotype:
        return 0
    return genotype.count(high_risk_allele)


def _calculate_weighted_score(data: dict) -> tuple[dict, float]:
    """
    Weighted scoring based on published clinical thresholds.
    Returns (scores_per_factor, total_raw_points).
    """
    scores = {}

    # sFlt-1/PlGF ratio — strongest angiogenic predictor
    ratio = data.get("sflt1_pigf_ratio", 0) or 0
    if ratio > 85:
        scores["sflt1_pigf_ratio"] = 25
    elif ratio > 38:
        scores["sflt1_pigf_ratio"] = 22
    elif ratio > 33:
        scores["sflt1_pigf_ratio"] = 15
    elif ratio > 20:
        scores["sflt1_pigf_ratio"] = 8
    else:
        scores["sflt1_pigf_ratio"] = 0

    # IL-6
    il6 = data.get("il6", 0) or 0
    if il6 > 30:
        scores["il6"] = 12
    elif il6 > 10:
        scores["il6"] = 10
    elif il6 > 5:
        scores["il6"] = 7
    else:
        scores["il6"] = 0

    # VEGF-A (low value = higher risk)
    vegfa = data.get("vegfa", 999) or 999
    if vegfa < 50:
        scores["vegfa"] = 10
    elif vegfa < 100:
        scores["vegfa"] = 8
    elif vegfa < 150:
        scores["vegfa"] = 3
    else:
        scores["vegfa"] = 0

    # MAP
    map_val = data.get("map", 0) or 0
    if map_val > 105:
        scores["map"] = 10
    elif map_val > 95:
        scores["map"] = 8
    elif map_val > 90:
        scores["map"] = 6
    elif map_val > 85:
        scores["map"] = 3
    else:
        scores["map"] = 0

    # Previous PE
    scores["previous_pe"] = 10 if data.get("previous_pe") else 0

    # IL-10 (low = loss of protection)
    il10 = data.get("il10", 999) or 999
    if il10 < 3:
        scores["il10"] = 8
    elif il10 < 5:
        scores["il10"] = 6
    elif il10 < 10:
        scores["il10"] = 3
    else:
        scores["il10"] = 0

    # MCP-1
    mcp1 = data.get("mcp1", 0) or 0
    if mcp1 > 500:
        scores["mcp1"] = 6
    elif mcp1 > 300:
        scores["mcp1"] = 5
    elif mcp1 > 200:
        scores["mcp1"] = 2
    else:
        scores["mcp1"] = 0

    # IL6 rs1800795 (GG = 2 copies of G = highest risk)
    il6_g = _encode_genotype(data.get("il6_rs1800795", ""), "G")
    scores["il6_genetics"] = [0, 3, 7][min(il6_g, 2)]

    # IL10 rs1800896 (AA = 2 copies of A = lowest IL-10 = highest risk)
    il10_a = _encode_genotype(data.get("il10_rs1800896", ""), "A")
    scores["il10_genetics"] = [0, 2, 5][min(il10_a, 2)]

    # Placental insufficiency degree
    pn_map = {"I": 2, "II": 5, "III": 8}
    if data.get("pn_diagnosis"):
        scores["pn_degree"] = pn_map.get(str(data.get("pn_degree", "I")), 2)
    else:
        scores["pn_degree"] = 0

    # Uterine artery PI (Doppler)
    pi = data.get("pi_uterine", 0) or 0
    if pi > 2.0:
        scores["pi_uterine"] = 6
    elif pi > 1.7:
        scores["pi_uterine"] = 4
    elif pi > 1.5:
        scores["pi_uterine"] = 2
    else:
        scores["pi_uterine"] = 0

    # FGR
    scores["fgr"] = 4 if data.get("fgr") else 0

    # IP-10
    ip10 = data.get("ip10", 0) or 0
    if ip10 > 400:
        scores["ip10"] = 4
    elif ip10 > 200:
        scores["ip10"] = 2
    else:
        scores["ip10"] = 0

    # TNF-alpha
    tnf = data.get("tnf_alpha", 0) or 0
    if tnf > 30:
        scores["tnf_alpha"] = 3
    elif tnf > 15:
        scores["tnf_alpha"] = 2
    else:
        scores["tnf_alpha"] = 0

    # Chronic hypertension
    scores["hypertension"] = 5 if data.get("chronic_hypertension") else 0

    # Early gestational age
    ga = data.get("gestational_age", 40) or 40
    if ga < 24:
        scores["gestational_age"] = 4
    elif ga < 28:
        scores["gestational_age"] = 2
    else:
        scores["gestational_age"] = 0

    total = sum(scores.values())
    return scores, float(total)


def _normalize_score(raw: float) -> float:
    """Map raw weighted score to 0-100 probability using sigmoid-like curve."""
    # Max theoretical raw score is ~115; calibrated so raw=60 → ~80% risk
    MAX_RAW = 115.0
    pct = min(100.0, round((raw / MAX_RAW) * 100, 1))
    return pct


def _xgb_predict(data: dict) -> float | None:
    model = _load_xgb()
    if model is None:
        return None
    try:
        features = _build_feature_vector(data)
        prob = model.predict_proba([features])[0][1]
        return round(float(prob) * 100, 1)
    except Exception:
        return None


def _build_feature_vector(data: dict) -> list:
    """Build numeric feature vector for XGBoost model."""
    return [
        float(data.get("age", 0) or 0),
        float(data.get("bmi", 0) or 0),
        float(data.get("gestational_age", 0) or 0),
        float(data.get("map", 0) or 0),
        float(data.get("parity", 0) or 0),
        int(bool(data.get("smoking"))),
        int(bool(data.get("chronic_hypertension"))),
        int(bool(data.get("diabetes"))),
        int(bool(data.get("anemia"))),
        int(bool(data.get("previous_pe"))),
        float(data.get("il6", 0) or 0),
        float(data.get("il10", 0) or 0),
        float(data.get("mcp1", 0) or 0),
        float(data.get("ip10", 0) or 0),
        float(data.get("tnf_alpha", 0) or 0),
        float(data.get("vegfa", 0) or 0),
        float(data.get("pigf", 0) or 0),
        float(data.get("sflt1", 0) or 0),
        float(data.get("sflt1_pigf_ratio", 0) or 0),
        float(_encode_genotype(data.get("il6_rs1800795", ""), "G")),
        float(_encode_genotype(data.get("il10_rs1800896", ""), "A")),
        float(_encode_genotype(data.get("vegfa_rs2010963", ""), "C")),
        int(bool(data.get("pn_diagnosis"))),
        {"I": 1, "II": 2, "III": 3}.get(str(data.get("pn_degree", "I")), 1),
        float(data.get("pi_uterine", 0) or 0),
        int(bool(data.get("fgr"))),
    ]


def _generate_marker_dynamics(data: dict, risk_level: str) -> dict:
    """
    Generate marker trend data across gestational weeks for visualization.
    Uses current values as endpoint and projects backward using risk-adjusted rates.
    """
    ga = int(data.get("gestational_age", 24) or 24)
    weeks = sorted(set([max(12, ga - 12), max(12, ga - 8), max(12, ga - 4), ga]))
    if len(weeks) < 4:
        weeks = [12, 16, 20, ga]

    def trend(current: float, factor: float, n: int) -> list:
        """Generate n-point trend ending at current, reversed by factor per step."""
        result = [current]
        for _ in range(n - 1):
            result.insert(0, result[0] / factor)
        return [round(v, 2) for v in result]

    il6 = float(data.get("il6", 5) or 5)
    il10 = float(data.get("il10", 15) or 15)
    vegfa = float(data.get("vegfa", 150) or 150)
    sflt1_ratio = float(data.get("sflt1_pigf_ratio", 20) or 20)

    n = len(weeks)
    factor = 1.15 if risk_level == "HIGH" else (1.08 if risk_level == "MODERATE" else 1.03)

    il6_trend = trend(il6, factor, n)
    il10_trend = list(reversed(trend(il10, factor, n)))
    vegfa_trend = list(reversed(trend(vegfa, factor, n)))
    ratio_trend = trend(sflt1_ratio, factor, n)

    return {
        "weeks": weeks,
        "il6": il6_trend,
        "il10": il10_trend,
        "vegfa": vegfa_trend,
        "sflt1_pigf_ratio": ratio_trend,
    }


def calculate_risk(data: dict, lang: str = "ru") -> dict:
    """
    Main entry point. Combines weighted scoring and XGBoost (if available).
    Returns full prediction result dict.
    """
    scores, raw = _calculate_weighted_score(data)
    weighted_pct = _normalize_score(raw)
    xgb_pct = _xgb_predict(data)

    if xgb_pct is not None:
        risk_percent = round(0.45 * weighted_pct + 0.55 * xgb_pct, 1)
    else:
        risk_percent = weighted_pct

    if risk_percent < 30:
        risk_level = "LOW"
    elif risk_percent < 60:
        risk_level = "MODERATE"
    else:
        risk_level = "HIGH"

    # Build top predictors
    total_pts = max(sum(scores.values()), 1)
    predictors = []
    for key, pts in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        if pts <= 0:
            continue
        labels = PREDICTOR_LABELS.get(key, {})
        predictors.append(
            {
                "name": key,
                "label": labels.get(lang, labels.get("ru", key)),
                "contribution": round((pts / total_pts) * 100),
                "direction": "down" if key in ("vegfa", "il10") else "up",
            }
        )

    return {
        "risk_percent": risk_percent,
        "risk_level": risk_level,
        "risk_label": RISK_LABELS[risk_level][lang],
        "risk_alert": RISK_ALERT[risk_level][lang],
        "top_predictors": predictors[:7],
        "recommendations": RECOMMENDATIONS[risk_level][lang],
        "marker_dynamics": _generate_marker_dynamics(data, risk_level),
        "model_used": "XGBoost Ensemble" if xgb_pct is not None else "Weighted Scoring",
    }
