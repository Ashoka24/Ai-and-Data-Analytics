# Clinical Data Analysis with Python

A reproducible clinical-data analysis project focused on data quality, exploratory analysis, descriptive statistics, subgroup comparisons, laboratory-result patterns and outcome associations. The workflow uses Python rather than BI dashboards.

> **Data notice:** All records are synthetic. Outcomes and laboratory reference bounds are illustrative and must not be interpreted as real clinical evidence, diagnostic guidance or validated healthcare benchmarks.

## Questions explored

- What does the encounter cohort look like by age band, sex, department and admission type?
- How do length of stay and encounter costs vary across departments and admission types?
- How do characteristics compare across the simulated readmission flag (a generated label, not verified follow-up)?
- How are synthetic lab results distributed, and how often do they fall outside example reference bounds?
- What data-quality issues should be checked before interpreting any clinical dataset?

## Methods

- Schema, missingness, duplicate-key, value-range and referential-integrity checks.
- Cohort profile and descriptive statistics.
- Grouped summaries for departments, admission types and months.
- Welch's t-test for exploratory length-of-stay comparisons between groups with different simulated flags.
- Chi-square test for association between department and simulated readmission status, where assumptions permit.
- Lab-result summaries by test type, including median, quartiles and example range flags.
- Correlation analysis for numeric fields, treated as exploratory rather than causal.
- Figures and machine-readable CSV/JSON outputs for reproducibility.

## Repository contents

- `data/encounters.csv`: 620 synthetic encounters.
- `data/lab_results.csv`: 2,480 synthetic lab-result rows.
- `scripts/analyze_clinical_data.py`: validation, statistical summaries and figure generation.
- `tests/test_clinical_data.py`: automated integrity and metric tests.
- `docs/data-dictionary.md`: variable definitions, data grain and limitations.
- `docs/analysis-plan.md`: questions, methods and interpretation guardrails.
- `outputs/`: generated tables, quality report, test results and figures (created when the script runs).

## Run the analysis

From the repository root:

```bash
python -m pip install -r requirements.txt
python clinical-data-analytics/scripts/analyze_clinical_data.py
python -m unittest discover -s clinical-data-analytics/tests -v
```

The script writes reproducible outputs under `clinical-data-analytics/outputs/`. It prints a compact summary and records the dataset's synthetic status in its outputs.

## Key outputs

- `data_quality_report.json` — missingness, duplicate IDs, referential integrity and range checks.
- `cohort_profile.csv` — encounter cohort characteristics.
- `department_summary.csv` — encounter count, length of stay, cost and simulated outcome summaries.
- `monthly_summary.csv` — monthly encounter volume and summary measures.
- `lab_summary.csv` — lab distributions and example out-of-range rates by test.
- `statistical_tests.json` — exploratory tests with sample sizes, estimates and p-values.
- `figures/` — distribution, subgroup and laboratory plots.

## Interpretation and limitations

This is a portfolio exercise using synthetic data, not a clinical study. A statistically significant result would not establish causation, clinical importance or generalizability. The readmission flag is simulated, lab reference bounds are simplified, and no risk adjustment or validated clinical definitions are provided. Real-world analysis requires approved data access, privacy safeguards, prespecified cohort definitions, missing-data handling, clinical review and domain-appropriate statistical methods.

## Privacy

Never commit identifiable patient information or protected health information. Use synthetic or appropriately approved de-identified data only.
