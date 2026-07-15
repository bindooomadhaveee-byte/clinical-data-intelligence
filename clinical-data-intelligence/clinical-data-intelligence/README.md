# Clinical Data Intelligence

A simple base project for clinical data analytics: it loads structured
patient records (CSV), runs them through a transparent, rule-based risk
scoring engine, and presents a population-health dashboard (risk
distribution, risk-by-age trends, top contributing risk factors, and a
high-risk patient worklist).

Unlike a black-box ML model, every risk score here is explainable — you can
see exactly which vitals/factors pushed a patient's score up, which is a
useful base to build a smarter model on top of later.

## Project structure

```
clinical-data-intelligence/
├── app.py               # Flask routes (dashboard + /api/summary, /api/patients)
├── data_loader.py        # CSV loading + synthetic sample data generator
├── risk_engine.py         # Rule-based 0-100 risk scoring per patient
├── insights.py             # Population-level aggregation (pure functions)
├── sample_data/
│   └── patients.csv         # Generated automatically on first run
├── templates/
│   └── index.html            # Dashboard UI (Chart.js)
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000. A synthetic dataset of 60 patients is generated
automatically on first run at `sample_data/patients.csv` — delete that file
and refresh to regenerate a new sample.

## How risk scoring works

`risk_engine.py` scores each patient 0-100 by checking how far key vitals
and clinical factors fall outside normal ranges:

| Factor | Normal range | Max points |
|---|---|---|
| Systolic BP | 90–130 mmHg | 15 |
| Diastolic BP | 60–85 mmHg | 10 |
| Heart rate | 60–100 bpm | 15 |
| Temperature | 36.1–37.5 °C | 15 |
| Glucose | 70–140 mg/dL | 15 |
| Condition count | scaled, cap at 5 conditions | 15 |
| Prior admissions (12mo) | scaled, cap at 3 | 10 |
| Age | ramps up after 60 | 5 |

Scores map to tiers: **Low** (<25), **Medium** (<50), **High** (<75),
**Critical** (≥75).

## Using your own data

Replace `sample_data/patients.csv` with a real (de-identified) dataset using
the same columns:

```
patient_id, age, gender, systolic_bp, diastolic_bp, heart_rate,
temperature_c, glucose_mg_dl, condition_count, prior_admissions_12mo,
length_of_stay_days
```

`load_patients()` in `data_loader.py` will pick it up automatically — no
other code changes needed.

## Extending the project

- **New risk factors**: add a normal range + weight in `risk_engine.py`,
  then include the field in your CSV / `data_loader.py`.
- **Swap in a real model**: replace `score_patient()`'s internals with a
  call to a trained classifier; keep the same return shape
  (`total_score`, `risk_level`, `factors`) so the dashboard keeps working.
- **FHIR integration**: pair this with the Smart FHIR Analytics project —
  map `Observation`/`Condition` resources into the same record shape used
  here instead of reading from CSV.
- **Alerts**: add a scheduled job that emails/pages when a patient crosses
  into the "Critical" tier.

## Notes

- `risk_engine.py` and `insights.py` are pure functions (no I/O), so they're
  easy to unit test with fixture data.
- This is a starting point, not a clinical decision-support system — the
  scoring weights are illustrative, not clinically validated. Any real
  deployment needs review by clinical stakeholders and appropriate
  regulatory/privacy handling (HIPAA, etc.) for real patient data.
