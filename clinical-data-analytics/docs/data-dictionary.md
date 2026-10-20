# Data dictionary

All records are synthetic and generated for this portfolio project. They are not real patient records, clinical advice or validated clinical quality data.

## data/encounters.csv

| Column | Meaning | Type |
|---|---|---|
| EncounterID | Unique synthetic encounter key | Text |
| PatientID | Synthetic patient key; may repeat across encounters | Text |
| EncounterDate | Encounter date | Date |
| Department | Service line | Category |
| AdmissionType | Emergency, elective, urgent or observation | Category |
| AgeBand | Age group, not exact age | Category |
| Sex | Synthetic category, includes not recorded | Category |
| LengthOfStayDays | Illustrative length of stay | Whole number |
| ICUFlag | 1 if ICU used in the synthetic encounter | Binary |
| SimulatedReadmissionFlag | Synthetic 30-day readmission indicator | Binary |
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
| ReferenceLow / ReferenceHigh | Example reference bounds for this synthetic exercise | Decimal |
| AbnormalFlag | 1 when result is outside example bounds | Binary |
| CollectedDate | Synthetic collection date | Date |

## Data grain

- Encounters: one row per EncounterID.
- Lab results: one row per lab result; multiple rows may belong to one encounter.
- Keep encounter-level and lab-level summaries separate unless an analysis explicitly accounts for repeated encounter rows.

## Important limitations

Readmission and outcome flags are simulated rather than clinically derived. Lab reference bounds are simplified and not intended to assess actual patients. These data are unsuitable for clinical decisions, research conclusions or institutional benchmarking.
