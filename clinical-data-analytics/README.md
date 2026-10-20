# Clinical Data Analytics — Power BI & Tableau

A portfolio project demonstrating clinical operations and laboratory-result analytics using **Power BI** and **Tableau**. It includes synthetic encounter and laboratory datasets, reproducible Python data-quality checks, dashboard measures, calculated fields, and build instructions for both BI tools.

> **Data notice:** Every record is synthetic. This is not real patient data, validated clinical quality data, or a clinical decision-support tool. Lab ranges and outcomes are simplified examples.

## Business questions

- How do encounter volume and service-line mix change over time?
- How does average length of stay vary by department and admission type?
- What are the simulated 30-day readmission, ICU-use and discharge-outcome rates?
- How do encounter costs vary by department and payer group?
- What share of simulated laboratory results fall outside example reference bounds?

## Project contents

- data/encounters.csv — 620 synthetic encounters with repeated synthetic patient IDs.
- data/lab_results.csv — 2,480 synthetic lab results across four test types.
- scripts/analyze_clinical_data.py — validates keys, flags, reference-range labels and exports summary tables.
- tests/test_clinical_data.py — unit tests for data integrity and metric bounds.
- power-bi/ClinicalMeasures.dax — DAX measures for encounter, cost, outcome and lab KPIs.
- power-bi/PowerQuery_M.m — Power Query import/type example.
- tableau/CalculatedFields.md — Tableau calculated fields and relationship guidance.
- docs/data-dictionary.md — field definitions, grain and caveats.

## Run validation and analysis

From the repository root:

    python -m pip install -r requirements.txt
    python clinical-data-analytics/scripts/analyze_clinical_data.py
    python -m unittest discover -s clinical-data-analytics/tests -v

Summary outputs are generated under clinical-data-analytics/outputs/ and are not committed.

## Build the Power BI report

1. Open Power BI Desktop and choose Get data → Text/CSV.
2. Import data/encounters.csv and data/lab_results.csv as separate tables.
3. In Power Query, confirm data types using power-bi/PowerQuery_M.m. Replace its example file path with your local path.
4. In Model view, create a one-to-many relationship from Encounters[EncounterID] to LabResults[EncounterID].
5. Add measures from power-bi/ClinicalMeasures.dax, creating each measure individually in Power BI's measure editor.
6. Create these report pages:

### Page 1 — Clinical Operations Overview
- KPI cards: Total Encounters, Unique Patients, Average Length of Stay, 30-Day Readmission Rate.
- Line chart: encounter count by month.
- Bar chart: encounters by department.
- Stacked bar: admission type by discharge disposition.
- Slicers: date, department, age band and admission type.

### Page 2 — Outcomes & Utilization
- KPI cards: ICU Encounter Rate, Expired Discharge Rate, Average Encounter Cost.
- Bar chart: readmission rate by department.
- Matrix: department by admission type with encounter count and average LOS.
- Slicers: date, diagnosis group and payer group.

### Page 3 — Laboratory Overview
- KPI cards: Lab Tests, Abnormal Lab Results, Abnormal Lab Result Rate.
- Bar chart: abnormal-result rate by lab test.
- Chart: result distribution against example reference bounds.
- Slicers: collection date and lab test.
- Keep lab-level measures separate from encounter-level measures to avoid duplicated counts.

## Build the Tableau workbook

1. Connect to data/encounters.csv in Tableau Desktop.
2. Add data/lab_results.csv as a second logical table related by EncounterID. Avoid a physical join that duplicates encounter rows.
3. Create calculated fields in tableau/CalculatedFields.md.
4. Build worksheets for monthly encounter trend, department volume, LOS by department, readmission rate, encounter cost, and abnormal lab rate.
5. Assemble three dashboards matching the Power BI pages above, with consistent date and department filters.
6. Save the workbook locally as Clinical_Data_Analytics.twbx after checking the data source paths.

## Metric definitions

- 30-day readmission rate: encounters flagged readmitted within 30 days divided by encounters.
- ICU encounter rate: encounters with ICUFlag = 1 divided by encounters.
- Expired discharge rate: encounters with DischargeDisposition = Expired divided by encounters.
- Abnormal lab result rate: out-of-range lab rows divided by all lab rows.

These measures describe this synthetic dataset only. Real clinical reporting requires approved definitions, cohort rules, governance, validation and clinical review.

## Privacy and responsible use

Use only approved, de-identified or synthetic datasets in portfolio work. Never commit PHI, patient names, medical record numbers, dates of birth or other identifiable records. Do not use these demonstration metrics for clinical decisions or institutional comparisons.
