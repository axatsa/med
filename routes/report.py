from flask import Blueprint, request, send_file, jsonify
import io
from models.database import db, Patient, Assessment

report_bp = Blueprint("report", __name__)


@report_bp.get("/report/<int:patient_id>")
def generate_report(patient_id: int):
    lang = request.args.get("lang", "ru")
    if lang not in ("ru", "uz"):
        lang = "ru"

    patient = db.get_or_404(Patient, patient_id)
    assessment = (
        Assessment.query.filter_by(patient_id=patient_id)
        .order_by(Assessment.created_at.desc())
        .first()
    )
    if assessment is None:
        return jsonify({"success": False, "error": "No assessment found for this patient"}), 404

    try:
        from utils.pdf_generator import generate_pdf
        pdf_bytes = generate_pdf(patient, assessment, lang=lang)
    except Exception as e:
        return jsonify({"success": False, "error": f"PDF generation failed: {str(e)}"}), 500

    filename = f"PE_Report_{patient_id}_{assessment.id}.pdf"
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@report_bp.get("/report/assessment/<int:assessment_id>")
def report_by_assessment(assessment_id: int):
    lang = request.args.get("lang", "ru")
    if lang not in ("ru", "uz"):
        lang = "ru"

    assessment = db.get_or_404(Assessment, assessment_id)
    patient = db.get_or_404(Patient, assessment.patient_id)

    try:
        from utils.pdf_generator import generate_pdf
        pdf_bytes = generate_pdf(patient, assessment, lang=lang)
    except Exception as e:
        return jsonify({"success": False, "error": f"PDF generation failed: {str(e)}"}), 500

    filename = f"PE_Report_{patient.id}_{assessment_id}.pdf"
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
