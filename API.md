# PE Predictor — API Reference

Base URL: `http://localhost:8000/api`  
CORS: enabled for all origins (`*`)

---

## POST /api/predict

Calculate risk and save patient to DB.

**Request body (JSON):**
```json
{
  "lang": "ru",
  "patient": {
    "full_name": "Иванова А.А.",
    "patient_code": "P-001"
  },
  "clinical": {
    "age": 29,
    "gestational_age": 24,
    "bmi": 26.4,
    "parity": 1,
    "smoking": false,
    "map": 95,
    "chronic_hypertension": false,
    "diabetes": false,
    "anemia": true,
    "previous_pe": false
  },
  "placental": {
    "diagnosis": true,
    "degree": "II",
    "pi_uterine": 1.85,
    "fgr": true
  },
  "immunological": {
    "il6": 86.7,
    "il10": 15.3,
    "mcp1": 312.4,
    "ip10": 284.6,
    "tnf_alpha": 18.6
  },
  "angiogenic": {
    "vegfa": 112.6,
    "pigf": 82.1,
    "sflt1": 3450,
    "sflt1_pigf_ratio": 42.1
  },
  "genetic": {
    "il6_rs1800795": "GG",
    "il10_rs1800896": "AA",
    "vegfa_rs2010963": "CT"
  }
}
```

**Response:**
```json
{
  "success": true,
  "patient_id": 1,
  "assessment_id": 1,
  "result": {
    "risk_percent": 85.3,
    "risk_level": "HIGH",
    "risk_label": "ВЫСОКИЙ РИСК",
    "risk_alert": "Высокая вероятность перехода...",
    "top_predictors": [
      {
        "name": "sflt1_pigf_ratio",
        "label": "Высокое соотношение sFlt-1/PlGF",
        "contribution": 28,
        "direction": "up"
      }
    ],
    "recommendations": ["Усиленный контроль АД...", "..."],
    "marker_dynamics": {
      "weeks": [12, 16, 20, 24],
      "il6": [57.01, 65.56, 75.39, 86.7],
      "il10": [15.3, 13.3, 11.57, 10.06],
      "vegfa": [112.6, 97.91, 85.14, 74.04],
      "sflt1_pigf_ratio": [27.68, 31.83, 36.61, 42.1]
    },
    "model_used": "XGBoost Ensemble"
  },
  "model_info": {
    "algorithm": "Weighted Scoring + XGBoost Ensemble",
    "auc": 0.89,
    "last_updated": "12.05.2025"
  }
}
```

**risk_level values:** `"LOW"` | `"MODERATE"` | `"HIGH"`  
**direction values:** `"up"` (bad, increased) | `"down"` (bad, decreased)  
**lang:** `"ru"` or `"uz"` — affects labels, recommendations, risk_label

---

## GET /api/patients

List all patients (paginated).

**Query params:**
- `page` (default: 1)
- `per_page` (default: 20)
- `search` — search by name or patient_code

**Response:**
```json
{
  "success": true,
  "patients": [...],
  "total": 42,
  "pages": 3,
  "page": 1
}
```

---

## GET /api/patients/:id

Get one patient with full data and all assessments.

---

## DELETE /api/patients/:id

Delete patient and all their assessments.

---

## GET /api/patients/:id/assessments

Get all assessment history for a patient (for dynamics chart).

---

## GET /api/stats

Returns counts by risk level.

```json
{
  "success": true,
  "total_patients": 15,
  "by_risk": {"HIGH": 8, "MODERATE": 5, "LOW": 2}
}
```

---

## GET /api/report/:patient_id?lang=ru

Download PDF report for latest assessment of patient.  
**Returns:** `application/pdf` binary

## GET /api/report/assessment/:assessment_id?lang=ru

Download PDF report for a specific assessment.

---

## GET /api/health

```json
{"status": "ok", "version": "1.0.0"}
```
