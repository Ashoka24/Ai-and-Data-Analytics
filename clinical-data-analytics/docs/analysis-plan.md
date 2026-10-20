# Analysis plan

## Scope

Describe the supplied synthetic encounter and laboratory datasets, assess data quality, summarize patterns and demonstrate a small number of exploratory statistical methods. This plan is not a clinical protocol.

## Primary questions

1. What is the cohort composition across departments, admission types, age bands and diagnosis groups?
2. How do length of stay and encounter cost distributions differ across operational groups?
3. Is length of stay different between records marked and not marked as readmitted in the simulated dataset?
4. Is department associated with the simulated 30-day readmission indicator?
5. How do laboratory values and example out-of-range flags vary by test type?

## Analysis methods

- Validate required fields, key uniqueness, missingness, binary flags, nonnegative cost and length-of-stay values, lab reference bounds, and encounter-to-lab referential integrity.
- Report counts, proportions, means, medians, standard deviations and quartiles as appropriate.
- Use Welch's two-sample t-test as an exploratory comparison of length of stay by simulated readmission flag.
- Use a chi-square test for department versus simulated readmission flag; report expected cell counts so sparse tables can be recognized.
- Calculate correlations only as exploratory summaries; do not infer causality.
- Generate plots for length-of-stay distribution, mean length of stay by department and example out-of-range lab rate by test.

## Interpretation rules

- A p-value is not a measure of effect size, clinical importance or causal evidence.
- The readmission indicator, lab values and reference bounds are simulated. Any observed differences are artifacts of this generated dataset and must not be generalized to patients or healthcare institutions.
- The current analysis does not adjust for confounding, assess missing-not-at-random mechanisms, validate outcome definitions or support clinical decisions.
- For real data, define the cohort and outcomes before analysis, review data provenance and missingness, select methods with clinical/statistical input, consider effect sizes and confidence intervals, and obtain appropriate privacy and governance approvals.
