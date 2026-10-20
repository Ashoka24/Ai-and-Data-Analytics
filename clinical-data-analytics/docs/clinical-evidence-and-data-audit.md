# Clinical Evidence and Data Validity Audit

**Audit date:** 2026-10-20

## Executive finding

This project currently contains **no real clinical evidence**. The encounter and laboratory CSVs are synthetic portfolio data, not sourced from an EHR, published study, registry, hospital or clinical trial. There is no external clinical dataset provenance, cohort protocol or reference-range provenance. The project demonstrates data handling and exploratory methods; it cannot substantiate clinical claims or be described as a clinical study.

## Dataset checks performed

| Check | Observed result | Assessment |
|---|---:|---|
| Encounter rows | 620 | Structural count only |
| Unique encounter IDs | 620 | Pass |
| Unique synthetic patient IDs | 440 | Generated structure; not evidence of real patients |
| Encounter date span | 2024-01-01 to 2025-11-29 | Provenance not established |
| Lab-result rows | 2,480 | Exactly four lab rows per encounter |
| Lab types | Hemoglobin, Creatinine, WBC, Glucose | Four repeated synthetic test types |
| Department distribution | Emergency 113; Neurology 113; General Medicine 113; Cardiology 113; Pulmonology 56; Orthopedics 56; Oncology 56 | Repeated/balanced counts are consistent with generated data, not a representative clinical sample |
| Readmission flag | 85 positive, 535 negative | Simulated; not clinically validated |
| Positive flags with a later same-patient encounter within 30 days in this file | 0 of 85 | Label cannot be verified from encounter chronology |
| Internal checks | Duplicate encounter IDs, missing key fields, orphan lab IDs, negative LOS/cost, reversed lab bounds, and flag consistency are checked by code | Internal consistency only; not clinical validity |

Exactly four lab rows occur per encounter: one each for hemoglobin, creatinine, WBC and glucose. This is a convenient synthetic design, not a real-world testing pattern. The data do not record glucose fasting status, collection context, assay/method provenance, or source-laboratory reference intervals.

## Laboratory reference-range review

| Test | Bounds in file | Validity assessment |
|---|---|---|
| Hemoglobin | 12–17 g/dL for every record | Not appropriate as a universal interval. Adult ranges can differ by sex and age and vary by laboratory. |
| Creatinine | 0.6–1.3 mg/dL for every record | Too simplified for universal interpretation. Results vary by person and laboratory; clinical interpretation requires context. |
| WBC | 4–11 × 10³/µL | Similar to a commonly quoted adult interval, but actual reporting-lab ranges should govern real data. |
| Glucose | 70–140 mg/dL for every record | Cannot be treated as a universal normal interval without knowing whether the sample was fasting, random or post-meal. |

These are plausibility observations, **not approval to use these bounds for patient interpretation**. MedlinePlus explains that hemoglobin ranges vary by sex/age and lab, creatinine varies by individual and laboratory, and glucose interpretation depends on the type and timing of the test.

Sources:
- Hemoglobin: https://medlineplus.gov/ency/article/003645.htm
- Creatinine: https://medlineplus.gov/lab-tests/creatinine-test/
- WBC: https://medlineplus.gov/ency/article/003643.htm
- Blood glucose: https://medlineplus.gov/ency/article/003482.htm

## What CI validates—and what it does not

Passing automated checks means the code executes and its programmed assertions pass. It does **not** verify clinical provenance, realistic patient distributions, validated outcome definitions, representative sampling, causal interpretation, reference intervals or compliance with a clinical study protocol.

## Required actions before claiming clinical validity

1. Keep the synthetic-data label visible in the README, data dictionary, figures and results.
2. Name the readmission outcome as a **simulated readmission flag**; do not present its percentage as a real readmission rate.
3. Label lab flags “outside illustrative bounds,” not “clinically abnormal.”
4. For a real-data project, select a documented, legally reusable public dataset or approved de-identified source; record source, version, license, inclusion criteria and data dictionary.
5. Use reference intervals from the reporting laboratory or dataset documentation, preserving units and demographic/test context.
6. Define readmission with an index encounter, outcome window, encounter types and exclusions. Validate against subsequent events; handle insufficient follow-up as unknown/censored rather than negative.
7. Before inferential claims, predefine hypotheses, assess missingness and sampling, report effect sizes and confidence intervals, check assumptions and obtain appropriate clinical/statistical review.

## Safe portfolio description

“Exploratory analysis of a synthetic healthcare dataset to demonstrate data-quality checks, cohort summaries, laboratory distribution plots and statistical testing. No real patient data or clinically validated findings are used.”
