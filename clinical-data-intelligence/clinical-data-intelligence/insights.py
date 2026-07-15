"""
insights.py
-----------
Population-level aggregation on top of raw records + risk scores.
Pure functions, no I/O — easy to unit test independently of Flask
or the risk engine's internals.
"""

from collections import Counter


def risk_level_distribution(scored_records):
    return dict(Counter(s["risk_level"] for s in scored_records))


def age_bucket(age):
    if age < 18:
        return "0-17"
    if age < 35:
        return "18-34"
    if age < 55:
        return "35-54"
    if age < 75:
        return "55-74"
    return "75+"


def average_risk_by_age_bucket(records, scored_records):
    by_id = {s["patient_id"]: s["total_score"] for s in scored_records}
    buckets = {}
    for r in records:
        b = age_bucket(r["age"])
        buckets.setdefault(b, []).append(by_id[r["patient_id"]])

    order = ["0-17", "18-34", "35-54", "55-74", "75+"]
    return {
        b: round(sum(buckets[b]) / len(buckets[b]), 1)
        for b in order if b in buckets
    }


def vital_summary(records, field):
    values = [r[field] for r in records]
    if not values:
        return {"min": None, "max": None, "avg": None}
    return {
        "min": min(values),
        "max": max(values),
        "avg": round(sum(values) / len(values), 1),
    }


def high_risk_patients(scored_records, threshold=50, limit=10):
    return [s for s in scored_records if s["total_score"] >= threshold][:limit]


def build_summary(records, scored_records, top_factors):
    return {
        "patient_count": len(records),
        "risk_distribution": risk_level_distribution(scored_records),
        "avg_risk_by_age": average_risk_by_age_bucket(records, scored_records),
        "vitals": {
            "systolic_bp": vital_summary(records, "systolic_bp"),
            "heart_rate": vital_summary(records, "heart_rate"),
            "glucose_mg_dl": vital_summary(records, "glucose_mg_dl"),
        },
        "top_risk_factors": top_factors,
        "high_risk_patients": high_risk_patients(scored_records),
    }
