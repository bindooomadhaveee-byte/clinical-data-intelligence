"""
data_loader.py
--------------
Loads clinical patient records from a CSV file. Also includes a
generator for synthetic sample data so the project runs out of the
box with no real patient data required.

Expected columns:
    patient_id, age, gender, systolic_bp, diastolic_bp, heart_rate,
    temperature_c, glucose_mg_dl, condition_count, prior_admissions_12mo,
    length_of_stay_days
"""

import csv
import os
import random

FIELDS = [
    "patient_id", "age", "gender", "systolic_bp", "diastolic_bp",
    "heart_rate", "temperature_c", "glucose_mg_dl", "condition_count",
    "prior_admissions_12mo", "length_of_stay_days",
]


def load_patients(csv_path):
    """Read a CSV file into a list of dicts with correctly typed fields."""
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append({
                "patient_id": row["patient_id"],
                "age": int(row["age"]),
                "gender": row["gender"],
                "systolic_bp": int(row["systolic_bp"]),
                "diastolic_bp": int(row["diastolic_bp"]),
                "heart_rate": int(row["heart_rate"]),
                "temperature_c": float(row["temperature_c"]),
                "glucose_mg_dl": int(row["glucose_mg_dl"]),
                "condition_count": int(row["condition_count"]),
                "prior_admissions_12mo": int(row["prior_admissions_12mo"]),
                "length_of_stay_days": int(row["length_of_stay_days"]),
            })
        return rows


def generate_sample_csv(path, n=60, seed=42):
    """Create a synthetic clinical dataset for demo purposes."""
    random.seed(seed)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for i in range(1, n + 1):
            age = random.randint(1, 95)
            # Older / sicker patients skew vitals worse, to make the demo meaningful
            severity = min(1.0, age / 100 + random.uniform(-0.15, 0.25))

            writer.writerow({
                "patient_id": f"P{i:04d}",
                "age": age,
                "gender": random.choice(["male", "female"]),
                "systolic_bp": int(110 + severity * 60 + random.uniform(-10, 10)),
                "diastolic_bp": int(70 + severity * 30 + random.uniform(-8, 8)),
                "heart_rate": int(70 + severity * 40 + random.uniform(-10, 10)),
                "temperature_c": round(36.5 + severity * 2.5 + random.uniform(-0.3, 0.3), 1),
                "glucose_mg_dl": int(90 + severity * 120 + random.uniform(-15, 15)),
                "condition_count": max(0, int(severity * 6 + random.uniform(-1, 1))),
                "prior_admissions_12mo": max(0, int(severity * 4 + random.uniform(-1, 1))),
                "length_of_stay_days": max(1, int(severity * 12 + random.uniform(-2, 2))),
            })
    return path


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "sample_data", "patients.csv")
    generate_sample_csv(out)
    print(f"Sample dataset written to {out}")
