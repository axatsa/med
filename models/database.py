from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Identity
    full_name = db.Column(db.String(200), nullable=True)
    patient_code = db.Column(db.String(50), nullable=True)

    # Clinical
    age = db.Column(db.Float)
    bmi = db.Column(db.Float)
    gestational_age = db.Column(db.Float)
    parity = db.Column(db.Integer)
    smoking = db.Column(db.Boolean, default=False)
    map_pressure = db.Column(db.Float)
    chronic_hypertension = db.Column(db.Boolean, default=False)
    diabetes = db.Column(db.Boolean, default=False)
    anemia = db.Column(db.Boolean, default=False)
    previous_pe = db.Column(db.Boolean, default=False)

    # Placental
    pn_diagnosis = db.Column(db.Boolean, default=False)
    pn_degree = db.Column(db.String(5))
    pi_uterine = db.Column(db.Float)
    fgr = db.Column(db.Boolean, default=False)

    # Immunological
    il6 = db.Column(db.Float)
    il10 = db.Column(db.Float)
    mcp1 = db.Column(db.Float)
    ip10 = db.Column(db.Float)
    tnf_alpha = db.Column(db.Float)

    # Angiogenic
    vegfa = db.Column(db.Float)
    pigf = db.Column(db.Float)
    sflt1 = db.Column(db.Float)
    sflt1_pigf_ratio = db.Column(db.Float)

    # Genetic
    il6_rs1800795 = db.Column(db.String(10))
    il10_rs1800896 = db.Column(db.String(10))
    vegfa_rs2010963 = db.Column(db.String(10))

    # Result
    risk_percent = db.Column(db.Float)
    risk_level = db.Column(db.String(20))
    model_used = db.Column(db.String(50))

    assessments = db.relationship("Assessment", backref="patient", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_assessments=False):
        d = {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "full_name": self.full_name,
            "patient_code": self.patient_code,
            "clinical": {
                "age": self.age,
                "bmi": self.bmi,
                "gestational_age": self.gestational_age,
                "parity": self.parity,
                "smoking": self.smoking,
                "map": self.map_pressure,
                "chronic_hypertension": self.chronic_hypertension,
                "diabetes": self.diabetes,
                "anemia": self.anemia,
                "previous_pe": self.previous_pe,
            },
            "placental": {
                "diagnosis": self.pn_diagnosis,
                "degree": self.pn_degree,
                "pi_uterine": self.pi_uterine,
                "fgr": self.fgr,
            },
            "immunological": {
                "il6": self.il6,
                "il10": self.il10,
                "mcp1": self.mcp1,
                "ip10": self.ip10,
                "tnf_alpha": self.tnf_alpha,
            },
            "angiogenic": {
                "vegfa": self.vegfa,
                "pigf": self.pigf,
                "sflt1": self.sflt1,
                "sflt1_pigf_ratio": self.sflt1_pigf_ratio,
            },
            "genetic": {
                "il6_rs1800795": self.il6_rs1800795,
                "il10_rs1800896": self.il10_rs1800896,
                "vegfa_rs2010963": self.vegfa_rs2010963,
            },
            "result": {
                "risk_percent": self.risk_percent,
                "risk_level": self.risk_level,
                "model_used": self.model_used,
            },
        }
        if include_assessments:
            d["assessments"] = [a.to_dict() for a in self.assessments]
        return d


class Assessment(db.Model):
    """Stores one risk calculation result linked to a patient."""

    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    gestational_age = db.Column(db.Float)
    risk_percent = db.Column(db.Float)
    risk_level = db.Column(db.String(20))
    top_predictors_json = db.Column(db.Text)
    recommendations_json = db.Column(db.Text)
    marker_dynamics_json = db.Column(db.Text)
    model_used = db.Column(db.String(50))

    def to_dict(self):
        import json

        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "gestational_age": self.gestational_age,
            "risk_percent": self.risk_percent,
            "risk_level": self.risk_level,
            "top_predictors": json.loads(self.top_predictors_json or "[]"),
            "recommendations": json.loads(self.recommendations_json or "[]"),
            "marker_dynamics": json.loads(self.marker_dynamics_json or "{}"),
            "model_used": self.model_used,
        }
        