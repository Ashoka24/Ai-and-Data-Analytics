"""Reproducible exploratory analysis of a synthetic clinical dataset."""
from __future__ import annotations
import json
from pathlib import Path
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "outputs"
FIGURES = OUTPUT / "figures"


def load_data():
    encounters = pd.read_csv(DATA / "encounters.csv", parse_dates=["EncounterDate"])
    labs = pd.read_csv(DATA / "lab_results.csv", parse_dates=["CollectedDate"])
    return encounters, labs


def validate_data(encounters: pd.DataFrame, labs: pd.DataFrame) -> list[str]:
    errors = []
    required_enc = {"EncounterID", "PatientID", "EncounterDate", "Department", "AdmissionType", "AgeBand", "Sex", "LengthOfStayDays", "ICUFlag", "SimulatedReadmissionFlag", "DischargeDisposition", "PrimaryDiagnosisGroup", "PayerGroup", "TotalCostUSD"}
    required_labs = {"EncounterID", "LabTest", "Result", "Unit", "ReferenceLow", "ReferenceHigh", "AbnormalFlag", "CollectedDate"}
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
    if (encounters["TotalCostUSD"] < 0).any():
        errors.append("TotalCostUSD cannot be negative.")
    for col in ["ICUFlag", "SimulatedReadmissionFlag"]:
        if not set(encounters[col].dropna().unique()).issubset({0, 1}):
            errors.append(f"{col} must contain only 0/1 values.")
    if set(labs["EncounterID"]) - set(encounters["EncounterID"]):
        errors.append("Lab results contain EncounterID values absent from encounters.")
    if labs[["Result", "ReferenceLow", "ReferenceHigh"]].isna().any().any():
        errors.append("Lab results and reference bounds must not be missing.")
    if (labs["ReferenceLow"] > labs["ReferenceHigh"]).any():
        errors.append("Lab reference lower bounds must not exceed upper bounds.")
    if not labs.empty:
        calculated = ((labs["Result"] < labs["ReferenceLow"]) | (labs["Result"] > labs["ReferenceHigh"])).astype(int)
        if not calculated.equals(labs["AbnormalFlag"].astype(int)):
            errors.append("AbnormalFlag does not match result/reference-range comparison.")
    return errors


def data_quality_report(encounters: pd.DataFrame, labs: pd.DataFrame) -> dict:
    return {
        "dataset_type": "synthetic demonstration data",
        "encounter_rows": int(len(encounters)),
        "lab_rows": int(len(labs)),
        "duplicate_encounter_ids": int(encounters["EncounterID"].duplicated().sum()),
        "encounter_missing_values": {k: int(v) for k, v in encounters.isna().sum().items()},
        "lab_missing_values": {k: int(v) for k, v in labs.isna().sum().items()},
        "orphan_lab_encounter_ids": int((~labs["EncounterID"].isin(encounters["EncounterID"])).sum()),
        "negative_length_of_stay_rows": int((encounters["LengthOfStayDays"] < 0).sum()),
        "negative_cost_rows": int((encounters["TotalCostUSD"] < 0).sum()),
        "invalid_lab_reference_bounds": int((labs["ReferenceLow"] > labs["ReferenceHigh"]).sum()),
        "validation_errors": validate_data(encounters, labs),
    }


def build_summaries(encounters: pd.DataFrame, labs: pd.DataFrame) -> dict:
    errors = validate_data(encounters, labs)
    if errors:
        raise ValueError("; ".join(errors))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    e = encounters.copy()
    e["Month"] = e["EncounterDate"].dt.to_period("M").dt.to_timestamp()

    quality = data_quality_report(e, labs)
    (OUTPUT / "data_quality_report.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")

    cohort = []
    for col in ["AgeBand", "Sex", "Department", "AdmissionType", "PrimaryDiagnosisGroup", "PayerGroup", "DischargeDisposition"]:
        part = e.groupby(col, dropna=False).agg(Encounters=("EncounterID", "nunique"), UniquePatients=("PatientID", "nunique"), MeanLOS=("LengthOfStayDays", "mean"), MedianLOS=("LengthOfStayDays", "median"), MeanCostUSD=("TotalCostUSD", "mean")).reset_index().rename(columns={col: "Category"})
        part.insert(0, "Characteristic", col)
        cohort.append(part)
    pd.concat(cohort, ignore_index=True).to_csv(OUTPUT / "cohort_profile.csv", index=False, float_format="%.3f")

    monthly = e.groupby("Month", as_index=False).agg(
        Encounters=("EncounterID", "nunique"), UniquePatients=("PatientID", "nunique"),
        MeanLOS=("LengthOfStayDays", "mean"), SimulatedReadmissionFlagCount=("SimulatedReadmissionFlag", "sum"),
        ICUEncounters=("ICUFlag", "sum"), TotalCostUSD=("TotalCostUSD", "sum"),
        ExpiredDischarges=("DischargeDisposition", lambda s: (s == "Expired").sum()))
    monthly["SimulatedReadmissionFlagPct"] = (monthly["SimulatedReadmissionFlagCount"] / monthly["Encounters"] * 100).round(2)
    monthly["ICURatePct"] = (monthly["ICUEncounters"] / monthly["Encounters"] * 100).round(2)
    monthly.to_csv(OUTPUT / "monthly_summary.csv", index=False, float_format="%.3f")

    department = e.groupby("Department", as_index=False).agg(
        Encounters=("EncounterID", "nunique"), UniquePatients=("PatientID", "nunique"),
        MeanLOS=("LengthOfStayDays", "mean"), MedianLOS=("LengthOfStayDays", "median"),
        MeanCostUSD=("TotalCostUSD", "mean"), TotalCostUSD=("TotalCostUSD", "sum"),
        SimulatedReadmissionFlagCount=("SimulatedReadmissionFlag", "sum"), ICUEncounters=("ICUFlag", "sum"))
    department["SimulatedReadmissionFlagPct"] = (department["SimulatedReadmissionFlagCount"] / department["Encounters"] * 100).round(2)
    department["ICURatePct"] = (department["ICUEncounters"] / department["Encounters"] * 100).round(2)
    department.to_csv(OUTPUT / "department_summary.csv", index=False, float_format="%.3f")

    lab_summary = labs.groupby(["LabTest", "Unit"], as_index=False).agg(
        TestCount=("Result", "size"), MeanResult=("Result", "mean"), MedianResult=("Result", "median"),
        SDResult=("Result", "std"), Q1=("Result", lambda s: s.quantile(.25)),
        Q3=("Result", lambda s: s.quantile(.75)), AbnormalResults=("AbnormalFlag", "sum"))
    lab_summary["AbnormalRatePct"] = (lab_summary["AbnormalResults"] / lab_summary["TestCount"] * 100).round(2)
    lab_summary.to_csv(OUTPUT / "lab_summary.csv", index=False, float_format="%.3f")

    tests = {}
    groups = [g["LengthOfStayDays"].dropna().to_numpy() for _, g in e.groupby("SimulatedReadmissionFlag")]
    if len(groups) == 2 and all(len(g) > 1 for g in groups):
        t = stats.ttest_ind(groups[0], groups[1], equal_var=False, nan_policy="omit")
        tests["welch_t_test_length_of_stay_by_readmission_flag"] = {
            "group_0_n": int(len(groups[0])), "group_1_n": int(len(groups[1])),
            "group_0_mean_days": round(float(groups[0].mean()), 4), "group_1_mean_days": round(float(groups[1].mean()), 4),
            "t_statistic": round(float(t.statistic), 5), "p_value": round(float(t.pvalue), 8),
            "interpretation_note": "Exploratory comparison on simulated data; not causal or clinically validated."
        }
    contingency = pd.crosstab(e["Department"], e["SimulatedReadmissionFlag"])
    if contingency.shape[0] > 1 and contingency.shape[1] > 1:
        chi = stats.chi2_contingency(contingency)
        tests["chi_square_department_by_readmission_flag"] = {
            "chi2_statistic": round(float(chi.statistic), 5), "degrees_of_freedom": int(chi.dof),
            "p_value": round(float(chi.pvalue), 8),
            "expected_cell_count_min": round(float(chi.expected_freq.min()), 3),
            "interpretation_note": "Association test on simulated data. Review expected counts; this does not imply causation."
        }
    (OUTPUT / "statistical_tests.json").write_text(json.dumps(tests, indent=2), encoding="utf-8")

    numeric = e[["LengthOfStayDays", "TotalCostUSD", "ICUFlag", "SimulatedReadmissionFlag"]].corr(numeric_only=True)
    numeric.to_csv(OUTPUT / "numeric_correlations.csv", float_format="%.4f")

    # Figures are saved for the repository report, not treated as clinical evidence.
    fig, ax = plt.subplots(figsize=(8, 4.5))
    e["LengthOfStayDays"].plot(kind="hist", bins=15, ax=ax)
    ax.set(title="Length of stay distribution (synthetic data)", xlabel="Length of stay (days)", ylabel="Encounter count")
    fig.tight_layout(); fig.savefig(FIGURES / "length_of_stay_distribution.png", dpi=140); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    department.sort_values("MeanLOS").plot(x="Department", y="MeanLOS", kind="barh", legend=False, ax=ax)
    ax.set(title="Mean length of stay by department", xlabel="Mean length of stay (days)", ylabel="")
    fig.tight_layout(); fig.savefig(FIGURES / "mean_los_by_department.png", dpi=140); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    lab_summary.plot(x="LabTest", y="AbnormalRatePct", kind="bar", legend=False, ax=ax)
    ax.set(title="Results outside example reference bounds", xlabel="Lab test", ylabel="Out-of-range results (%)")
    fig.tight_layout(); fig.savefig(FIGURES / "lab_out_of_range_rate.png", dpi=140); plt.close(fig)

    summary = {
        "dataset_type": "synthetic demonstration data",
        "encounters": int(e["EncounterID"].nunique()),
        "unique_patients": int(e["PatientID"].nunique()),
        "mean_length_of_stay_days": round(float(e["LengthOfStayDays"].mean()), 2),
        "median_length_of_stay_days": round(float(e["LengthOfStayDays"].median()), 2),
        "simulated_readmission_flag_pct": round(float(e["SimulatedReadmissionFlag"].mean() * 100), 2),
        "icu_encounter_rate_pct": round(float(e["ICUFlag"].mean() * 100), 2),
        "lab_results": int(len(labs)),
        "lab_abnormal_rate_pct": round(float(labs["AbnormalFlag"].mean() * 100), 2),
        "date_min": str(e["EncounterDate"].min().date()), "date_max": str(e["EncounterDate"].max().date()),
        "validation_errors": errors,
        "outputs_directory": str(OUTPUT.relative_to(ROOT.parent)),
    }
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main():
    encounters, labs = load_data()
    summary = build_summaries(encounters, labs)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
