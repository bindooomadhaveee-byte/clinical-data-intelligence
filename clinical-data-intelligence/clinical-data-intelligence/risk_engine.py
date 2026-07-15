"""
risk_engine.py
--------------
A transparent, rule-based risk scoring engine. Each vital / clinical
factor contributes points if it falls outside a normal range; points
are summed into a 0-100 score and mapped to a risk tier.

This is intentionally simple and explainable (not ML) so it's a good
base to extend later with a trained model, while still being useful
for demoing population health triage.
"""

NORMAL_RANGES = {
    "systolic_bp": (90, 130),
    "diastolic_bp": (60, 85),
    "heart_rate": (60, 100),
    "temperature_c": (36.1, 37.5),
    "glucose_mg_dl": (70, 140),
}

# Max points each factor can contribute to the 0-100 score
WEIGHTS = {
    "systolic_bp": 15,
    "diastolic_bp": 10,
    "heart_rate": 15,
    "temperature_c": 15,
    "glucose_mg_dl": 15,
    "condition_count": 15,
    "prior_admissions_12mo": 10,
    "age": 5,
}


def _out_of_range_severity(value, low, high):
    """Return 0..1 severity of how far outside [low, high] the value is."""
    if low <= value <= high:
        return 0.0
    span = high - low
    if value < low:
        return min(1.0, (low - value) / span)
    return min(1.0, (value - high) / span)


def score_patient(record):
    """
    Compute a 0-100 risk score and breakdown for a single patient record.
    Returns dict: { total_score, risk_level, factors: {name: points} }
    """
    factors = {}

    for vital, (low, high) in NORMAL_RANGES.items():
        severity = _out_of_range_severity(record[vital], low, high)
        factors[vital] = round(severity * WEIGHTS[vital], 1)

    # Comorbidity burden: each condition adds risk, capped at weight
    factors["condition_count"] = round(
        min(1.0, record["condition_count"] / 5) * WEIGHTS["condition_count"], 1
    )

    # Prior admissions strongly predict readmission risk
    factors["prior_admissions_12mo"] = round(
        min(1.0, record["prior_admissions_12mo"] / 3) * WEIGHTS["prior_admissions_12mo"], 1
    )

    # Age risk ramps up gradually after 60
    age_factor = max(0.0, (record["age"] - 60) / 40)
    factors["age"] = round(min(1.0, age_factor) * WEIGHTS["age"], 1)

    total = round(sum(factors.values()), 1)
    total = min(100.0, total)

    if total < 25:
        level = "Low"
    elif total < 50:
        level = "Medium"
    elif total < 75:
        level = "High"
    else:
        level = "Critical"

    return {
        "patient_id": record["patient_id"],
        "total_score": total,
        "risk_level": level,
        "factors": factors,
    }


def score_population(records):
    """Score every record; return list sorted by risk score descending."""
    scored = [score_patient(r) for r in records]
    return sorted(scored, key=lambda s: s["total_score"], reverse=True)


def top_risk_factors(scored_records, n=5):
    """
    Aggregate which factors contribute most risk across the population,
    useful for spotting systemic issues (e.g. glucose control).
    """
    totals = {}
    for s in scored_records:
        for factor, points in s["factors"].items():
            totals[factor] = totals.get(factor, 0) + points
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    return [(name, round(pts, 1)) for name, pts in ranked[:n]]
