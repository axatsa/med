import json
from flask import Blueprint, request, jsonify
from models.database import db, Patient, Assessment
from models.risk_calculator import calculate_risk
from config import Config

predict_bp = Blueprint("predict", __name__)


def _flatten_input(body: dict) -> dict:
    """Flatten nested request body into a single dict for the calculator."""
    clinical = body.get("clinical", {})
    placental = body.get("placental", {})
    immuno = body.get("immunological", {})
    angio = body.get("angiogenic", {})
    genetic = body.get("genetic", {})

    return {
        # Clinical
        "age": clinical.get("age"),
        "bmi": clinical.get("bmi"),
        "gestational_age": clinical.get("gestational_age"),
        "parity": clinical.get("parity"),
        "smoking": clinical.get("smoking", False),
        "map": clinical.get("map"),
        "chronic_hypertension": clinical.get("chronic_hypertension", False),
        "diabetes": clinical.get("diabetes", False),
        "anemia": clinical.get("anemia", False),
        "previous_pe": clinical.get("previous_pe", False),
        # Placental
        "pn_diagnosis": placental.get("diagnosis", False),
        "pn_degree": placental.get("degree", "I"),
        "pi_uterine": placental.get("pi_uterine"),
        "fgr": placental.get("fgr", False),
        # Immunological
        "il6": immuno.get("il6"),
        "il10": immuno.get("il10"),
        "mcp1": immuno.get("mcp1"),
        "ip10": immuno.get("ip10"),
        "tnf_alpha": immuno.get("tnf_alpha"),
        # Angiogenic
        "vegfa": angio.get("vegfa"),
        "pigf": angio.get("pigf"),
        "sflt1": angio.get("sflt1"),
        "sflt1_pigf_ratio": angio.get("sflt1_pigf_ratio"),
        # Genetic
        "il6_rs1800795": genetic.get("il6_rs1800795", ""),
        "il10_rs1800896": genetic.get("il10_rs1800896", ""),
        "vegfa_rs2010963": genetic.get("vegfa_rs2010963", ""),
    }


@predict_bp.post("/predict")
def predict():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"success": False, "error": "Empty request body"}), 400

    lang = body.get("lang", "ru")
    if lang not in ("ru", "uz"):
        lang = "ru"

    flat = _flatten_input(body)
    result = calculate_risk(flat, lang)

    # Optionally persist patient + assessment
    patient_info = body.get("patient", {})
    patient_id = None

    try:
        patient = Patient(
            full_name=patient_info.get("full_name"),
            patient_code=patient_info.get("patient_code"),
            age=flat.get("age"),
            bmi=flat.get("bmi"),
            gestational_age=flat.get("gestational_age"),
            parity=flat.get("parity"),
            smoking=flat.get("smoking"),
            map_pressure=flat.get("map"),
            chronic_hypertension=flat.get("chronic_hypertension"),
            diabetes=flat.get("diabetes"),
            anemia=flat.get("anemia"),
            previous_pe=flat.get("previous_pe"),
            pn_diagnosis=flat.get("pn_diagnosis"),
            pn_degree=flat.get("pn_degree"),
            pi_uterine=flat.get("pi_uterine"),
            fgr=flat.get("fgr"),
            il6=flat.get("il6"),
            il10=flat.get("il10"),
            mcp1=flat.get("mcp1"),
            ip10=flat.get("ip10"),
            tnf_alpha=flat.get("tnf_alpha"),
            vegfa=flat.get("vegfa"),
            pigf=flat.get("pigf"),
            sflt1=flat.get("sflt1"),
            sflt1_pigf_ratio=flat.get("sflt1_pigf_ratio"),
            il6_rs1800795=flat.get("il6_rs1800795"),
            il10_rs1800896=flat.get("il10_rs1800896"),
            vegfa_rs2010963=flat.get("vegfa_rs2010963"),
            risk_percent=result["risk_percent"],
            risk_level=result["risk_level"],
            model_used=result["model_used"],
        )
        db.session.add(patient)
        db.session.flush()

        assessment = Assessment(
            patient_id=patient.id,
            gestational_age=flat.get("gestational_age"),
            risk_percent=result["risk_percent"],
            risk_level=result["risk_level"],
            top_predictors_json=json.dumps(result["top_predictors"], ensure_ascii=False),
            recommendations_json=json.dumps(result["recommendations"], ensure_ascii=False),
            marker_dynamics_json=json.dumps(result["marker_dynamics"], ensure_ascii=False),
            model_used=result["model_used"],
        )
        db.session.add(assessment)
        db.session.commit()
        patient_id = patient.id
        assessment_id = assessment.id
    except Exception as e:
        db.session.rollback()
        patient_id = None
        assessment_id = None

    return jsonify(
        {
            "success": True,
            "patient_id": patient_id,
            "assessment_id": assessment_id,
            "result": result,
            "model_info": {
                "algorithm": Config.MODEL_ALGORITHM,
                "auc": Config.MODEL_AUC,
                "last_updated": Config.MODEL_LAST_UPDATED,
            },
        }
    )
