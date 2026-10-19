# Customer Churn Prediction

This project explores which customer characteristics are associated with churn and compares two classification models: logistic regression and random forest. It includes a reproducible Python workflow, a held-out test set, evaluation metrics, ranked model features, and a small Streamlit dashboard.

**Data disclaimer:** `data/customer_churn.csv` is synthetic data generated for this project. It does not represent a real telecom provider or real customers. Metrics and patterns are demonstrations of the analysis workflow, not evidence about an actual business.

## Questions

- What proportion of customers churn in the sample?
- How do contract type, tenure, support services and payment method relate to churn?
- Does logistic regression or random forest perform better on the same held-out customers?
- How do precision, recall, F1-score and ROC-AUC compare?
- Which features are most influential in each model?

## Methods

- Stratified 80/20 train/test split with a fixed random seed.
- Numeric and categorical preprocessing inside scikit-learn pipelines.
- Logistic regression with class weighting and a random forest with balanced class weights.
- Evaluation on the held-out test set using accuracy, precision, recall, F1-score and ROC-AUC.
- Confusion matrices and model-specific feature rankings.

The test set is not used to fit the preprocessing steps or models. The feature rankings are model explanations, not causal effects. Because the data is synthetic, the project should not be used to make real retention decisions.

## Project structure

```text
customer-churn-prediction/
├── data/customer_churn.csv
├── scripts/run_analysis.py
├── sql/churn_analysis.sql
├── tests/test_churn.py
├── app.py
└── README.md
```

## Run locally

From the repository root:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python projects/customer-churn-prediction/scripts/run_analysis.py
python -m unittest discover -s projects/customer-churn-prediction/tests -v
streamlit run projects/customer-churn-prediction/app.py
```

Linux, macOS or WSL:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python projects/customer-churn-prediction/scripts/run_analysis.py
python -m unittest discover -s projects/customer-churn-prediction/tests -v
streamlit run projects/customer-churn-prediction/app.py
```

The script writes reproducible outputs to `projects/customer-churn-prediction/outputs/`:

- `model_metrics.csv`
- `classification_report_logistic_regression.csv`
- `classification_report_random_forest.csv`
- `confusion_matrix_logistic_regression.csv`
- `confusion_matrix_random_forest.csv`
- `feature_importance_logistic_regression.csv`
- `feature_importance_random_forest.csv`
- `churn_by_contract.csv`
- `roc_curves.png`
- `key_findings.md`

Generated outputs are not committed. Re-run the script to recreate them from the CSV.

## SQL

The queries in `sql/churn_analysis.sql` cover churn rate by contract, tenure band, internet service and payment method. They are descriptive summaries; differences do not establish causation.

## Dashboard

After running the analysis, start the optional Streamlit app with the command above. It provides sample-level KPIs, churn breakdowns and model comparison metrics.

## Licence

MIT. The root repository's MIT licence applies to this project as well.
