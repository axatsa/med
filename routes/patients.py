from flask import Blueprint, request, jsonify
from models.database import db, Patient, Assessment

patients_bp = Blueprint("patients", __name__)


@patients_bp.get("/patients")
def list_patients():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search = request.args.get("search", "").strip()

    query = Patient.query.order_by(Patient.created_at.desc())
    if search:
        query = query.filter(
            db.or_(
                Patient.full_name.ilike(f"%{search}%"),
                Patient.patient_code.ilike(f"%{search}%"),
            )
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(
        {
            "success": True,
            "patients": [p.to_dict() for p in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "page": page,
        }
    )


@patients_bp.get("/patients/<int:patient_id>")
def get_patient(patient_id: int):
    patient = db.get_or_404(Patient, patient_id)
    return jsonify({"success": True, "patient": patient.to_dict(include_assessments=True)})


@patients_bp.delete("/patients/<int:patient_id>")
def delete_patient(patient_id: int):
    patient = db.get_or_404(Patient, patient_id)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({"success": True, "message": f"Patient {patient_id} deleted"})


@patients_bp.get("/patients/<int:patient_id>/assessments")
def get_assessments(patient_id: int):
    db.get_or_404(Patient, patient_id)
    assessments = (
        Assessment.query.filter_by(patient_id=patient_id)
        .order_by(Assessment.created_at.desc())
        .all()
    )
    return jsonify({"success": True, "assessments": [a.to_dict() for a in assessments]})


@patients_bp.get("/stats")
def stats():
    total = Patient.query.count()
    high = Patient.query.filter_by(risk_level="HIGH").count()
    moderate = Patient.query.filter_by(risk_level="MODERATE").count()
    low = Patient.query.filter_by(risk_level="LOW").count()
    return jsonify(
        {
            "success": True,
            "total_patients": total,
            "by_risk": {"HIGH": high, "MODERATE": moderate, "LOW": low},
        }
    )
