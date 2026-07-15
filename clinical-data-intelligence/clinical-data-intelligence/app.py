"""
app.py
------
Flask entry point for the Clinical Data Intelligence dashboard.

Run:
    pip install -r requirements.txt
    python app.py
Then open http://localhost:5000

On first run, if sample_data/patients.csv doesn't exist yet, a
synthetic dataset is generated automatically so the dashboard works
immediately.
"""

import os

from flask import Flask, jsonify, render_template

from data_loader import generate_sample_csv, load_patients
from insights import build_summary
from risk_engine import score_population, top_risk_factors

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "sample_data", "patients.csv")


def ensure_sample_data():
    if not os.path.exists(DATA_PATH):
        generate_sample_csv(DATA_PATH)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/summary")
def summary():
    ensure_sample_data()
    try:
        records = load_patients(DATA_PATH)
    except Exception as exc:  # noqa: BLE001 - surface parse/IO errors to the UI
        return jsonify({"error": str(exc)}), 500

    scored = score_population(records)
    factors = top_risk_factors(scored)
    return jsonify(build_summary(records, scored, factors))


@app.route("/api/patients")
def patients():
    """Full ranked patient list with risk scores (for a drill-down table)."""
    ensure_sample_data()
    records = load_patients(DATA_PATH)
    return jsonify(score_population(records))


if __name__ == "__main__":
    ensure_sample_data()
    app.run(debug=True, port=5000)
