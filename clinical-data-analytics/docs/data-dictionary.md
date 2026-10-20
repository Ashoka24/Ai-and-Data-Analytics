# Data dictionary

All rows are **synthetic and generated for this portfolio project**. They are not real patient records, clinical advice, or validated clinical quality data.

## data/encounters.csv

| Column | Meaning | Type |
|---|---|---|
| EncounterID | Unique synthetic encounter key | Text |
| PatientID | Synthetic patient key; may repeat | Text |
| EncounterDate | Encounter date | Date |
| Department | Service line | Category |
| AdmissionType | Emergency, elective, urgent or observation | Category |
| AgeBand | Age group, not exact age | Category |
| Sex | Synthetic category, includes not recorded | Category |
| LengthOfStayDays | Illustrative length of stay | Whole number |
| ICUFlag | 1 if ICU used in the synthetic encounter | Binary |
| Readmitted30Days | Synthetic 30-day readmission indicator | Binary |
| DischargeDisposition | Synthetic discharge category | Category |
| PrimaryDiagnosisGroup | Broad diagnosis group | Category |
| PayerGroup | Synthetic payer category | Category |
| TotalCostUSD | Illustrative encounter cost in USD | Numeric |

## data/lab_results.csv

| Column | Meaning | Type |
|---|---|---|
| EncounterID | Links result to an encounter | Text |
| LabTest | Hemoglobin, creatinine, WBC or glucose | Category |
| Result | Synthetic lab result | Decimal |
| Unit | Measurement unit | Text |
| ReferenceLow / ReferenceHigh | Demo reference bounds | Decimal |
| AbnormalFlag | 1 when result is outside demo bounds | Binary |
| CollectedDate | Synthetic collection date | Date |

## Grain and relationships

- Encounters: one row per EncounterID.
- Lab results: one row per lab test per encounter; multiple rows per encounter.
- Recommended relationship: Encounters[EncounterID] one-to-many LabResults[EncounterID].
- Avoid physically joining lab rows into encounters before calculating encounter-level counts, rates or costs; repeated rows distort measures.

## Important limitations

Readmission and outcome flags are simulated rather than clinically derived. Lab reference bounds are simplified and not intended to assess actual patients. Do not use this data for clinical decisions, research conclusions or institutional benchmarking.
