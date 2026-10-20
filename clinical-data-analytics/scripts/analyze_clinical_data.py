"""Validate synthetic clinical data and export dashboard-ready summaries."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "outputs"

def load_data():
    encounters = pd.read_csv(DATA / "encounters.csv", parse_dates=["EncounterDate"])
    labs = pd.read_csv(DATA / "lab_results.csv", parse_dates=["CollectedDate"])
    return encounters, labs

def validate_data(encounters: pd.DataFrame, labs: pd.DataFrame) -> list[str]:
    errors = []
    required_enc = {"EncounterID", "PatientID", "EncounterDate", "Department", "LengthOfStayDays", "ICUFlag", "Readmitted30Days", "DischargeDisposition", "TotalCostUSD"}
    required_labs = {"EncounterID", "LabTest", "Result", "ReferenceLow", "ReferenceHigh", "AbnormalFlag", "CollectedDate"}
    if not required_enc.issubset(encounters.columns):
        errors.append(f"Encounter columns missing: {sorted(required_enc - set(encounters.columns))}")
    if not required_labs.issubset(labs.columns):
        errors.append(f"Lab columns missing: {sorted(required_labs - set(labs.columns))}")
    if errors:
        return errors
    if encounters["EncounterID"].duplicated().any():
        errors.append("EncounterID must be unique in encounters.")
    if encounters[["EncounterID", "PatientID", "EncounterDate"]].isna().any().any():
        errors.append("Encounter identifiers and dates must not be missing.")
    if (encounters["LengthOfStayDays"] < 0).any():
        errors.append("LengthOfStayDays cannot be negative.")
    for col in ["ICUFlag", "Readmitted30Days"]:
        if not set(encounters[col].dropna().unique()).issubset({0, 1}):
            errors.append(f"{col} must contain only 0/1 values.")
    if (encounters["TotalCostUSD"] < 0).any():
        errors.append("TotalCostUSD cannot be negative.")
    if set(labs["EncounterID"]) - set(encounters["EncounterID"]):
        errors.append("Lab results contain EncounterID values absent from encounters.")
    if labs[["Result", "ReferenceLow", "ReferenceHigh"]].isna().any().any():
        errors.append("Lab results and reference bounds must not be missing.")
    if not labs.empty:
        calculated = ((labs["Result"] < labs["ReferenceLow"]) | (labs["Result"] > labs["ReferenceHigh"])).astype(int)
        if not calculated.equals(labs["AbnormalFlag"].astype(int)):
            errors.append("AbnormalFlag does not match result/reference-range comparison.")
    return errors

def build_summaries(encounters: pd.DataFrame, labs: pd.DataFrame) -> dict:
    if errors := validate_data(encounters, labs):
        raise ValueError("; ".join(errors))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    e = encounters.copy()
    e["Month"] = e["EncounterDate"].dt.to_period("M").dt.to_timestamp()
    monthly = e.groupby("Month", as_index=False).agg(
        Encounters=("EncounterID", "nunique"), UniquePatients=("PatientID", "nunique"),
        MeanLOS=("LengthOfStayDays", "mean"), Readmissions30D=("Readmitted30Days", "sum"),
        ICUEncounters=("ICUFlag", "sum"), TotalCostUSD=("TotalCostUSD", "sum"),
        MortalityEncounters=("DischargeDisposition", lambda s: (s == "Expired").sum()))
    monthly["ReadmissionRatePct"] = (monthly["Readmissions30D"] / monthly["Encounters"] * 100).round(2)
    monthly["ICURatePct"] = (monthly["ICUEncounters"] / monthly["Encounters"] * 100).round(2)
    monthly["MortalityRatePct"] = (monthly["MortalityEncounters"] / monthly["Encounters"] * 100).round(2)
    department = e.groupby("Department", as_index=False).agg(
        Encounters=("EncounterID", "nunique"), MeanLOS=("LengthOfStayDays", "mean"),
        Readmissions30D=("Readmitted30Days", "sum"), ICUEncounters=("ICUFlag", "sum"),
        TotalCostUSD=("TotalCostUSD", "sum"))
    department["ReadmissionRatePct"] = (department["Readmissions30D"] / department["Encounters"] * 100).round(2)
    lab_summary = labs.groupby(["LabTest", "Unit"], as_index=False).agg(
        TestCount=("EncounterID", "size"), AbnormalResults=("AbnormalFlag", "sum"), MeanResult=("Result", "mean"))
    lab_summary["AbnormalRatePct"] = (lab_summary["AbnormalResults"] / lab_summary["TestCount"] * 100).round(2)
    monthly.to_csv(OUTPUT / "monthly_summary.csv", index=False, float_format="%.2f")
    department.to_csv(OUTPUT / "department_summary.csv", index=False, float_format="%.2f")
    lab_summary.to_csv(OUTPUT / "lab_summary.csv", index=False, float_format="%.2f")
    summary = {
        "dataset_type": "synthetic demonstration data",
        "encounters": int(e["EncounterID"].nunique()),
        "unique_patients": int(e["PatientID"].nunique()),
        "mean_length_of_stay_days": round(float(e["LengthOfStayDays"].mean()), 2),
        "readmission_30d_rate_pct": round(float(e["Readmitted30Days"].mean() * 100), 2),
        "icu_encounter_rate_pct": round(float(e["ICUFlag"].mean() * 100), 2),
        "expired_discharge_rate_pct": round(float((e["DischargeDisposition"] == "Expired").mean() * 100), 2),
        "lab_results": int(len(labs)),
        "lab_abnormal_rate_pct": round(float(labs["AbnormalFlag"].mean() * 100), 2),
        "date_min": str(e["EncounterDate"].min().date()), "date_max": str(e["EncounterDate"].max().date()),
        "validation_errors": []}
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary

def main():
    encounters, labs = load_data()
    print(json.dumps(build_summaries(encounters, labs), indent=2))
if __name__ == "__main__":
    main()
