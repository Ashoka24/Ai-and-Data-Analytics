# Tableau calculated fields

Connect Tableau Desktop to the synthetic encounters CSV as the primary table. Add the laboratory CSV as a second logical table related by EncounterID. Prefer a logical relationship over a physical join that multiplies encounter rows.

## Encounter-level fields

### Total Encounters
~~~tableau
COUNTD([EncounterID])
~~~

### Unique Patients
~~~tableau
COUNTD([PatientID])
~~~

### Average Length of Stay
~~~tableau
AVG([LengthOfStayDays])
~~~

### 30-Day Readmission Rate
~~~tableau
SUM(IIF([Readmitted30Days] = 1, 1, 0)) / COUNTD([EncounterID])
~~~
Format as Percentage.

### ICU Encounter Rate
~~~tableau
SUM(IIF([ICUFlag] = 1, 1, 0)) / COUNTD([EncounterID])
~~~
Format as Percentage.

### Expired Discharge Rate
~~~tableau
SUM(IIF([DischargeDisposition] = "Expired", 1, 0)) / COUNTD([EncounterID])
~~~
Format as Percentage.

### Total Encounter Cost
~~~tableau
SUM([TotalCostUSD])
~~~

### Average Encounter Cost
~~~tableau
SUM([TotalCostUSD]) / COUNTD([EncounterID])
~~~

## Lab-level fields

If lab results are used in a separate data source:

### Abnormal Lab Result Rate
~~~tableau
SUM(IIF([AbnormalFlag] = 1, 1, 0)) / COUNT([Result])
~~~
Format as Percentage.

### Lab Test Count
~~~tableau
COUNT([Result])
~~~

### Out-of-range Result
~~~tableau
IF [Result] < [ReferenceLow] OR [Result] > [ReferenceHigh]
THEN "Out of range"
ELSE "Within reference range"
END
~~~

## Dashboard filters

- Encounter date range
- Department
- Admission type
- Age band
- Sex (including Not recorded)
- Primary diagnosis group
- Discharge disposition

Use consistent filter scope across encounter worksheets. Do not use lab-level row counts to calculate encounter-level rates after a physical join. These fields describe synthetic data and are not clinical decision rules.
