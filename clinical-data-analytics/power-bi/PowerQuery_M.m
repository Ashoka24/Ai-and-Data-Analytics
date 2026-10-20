// Power Query M example for the Encounters table in Power BI Desktop.
// Import via Get Data > Text/CSV, then replace this example path with your local path.
let
    Source = Csv.Document(
        File.Contents("C:\YOUR\PATH\clinical-data-analytics\data\encounters.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"EncounterID", type text}, {"PatientID", type text}, {"EncounterDate", type date},
        {"Department", type text}, {"AdmissionType", type text}, {"AgeBand", type text},
        {"Sex", type text}, {"LengthOfStayDays", Int64.Type}, {"ICUFlag", Int64.Type},
        {"Readmitted30Days", Int64.Type}, {"DischargeDisposition", type text},
        {"PrimaryDiagnosisGroup", type text}, {"PayerGroup", type text}, {"TotalCostUSD", Currency.Type}
    })
in
    Types

// Repeat for LabResults using data/lab_results.csv.
// Type EncounterID, LabTest and Unit as text; Result and reference bounds as decimal;
// AbnormalFlag as whole number; CollectedDate as date.
