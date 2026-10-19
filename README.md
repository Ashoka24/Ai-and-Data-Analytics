# Sales Performance & Business Intelligence

A small end-to-end analytics project built around a retail sales dataset. It takes raw order records, validates and enriches them with Python, stores the result in SQLite, answers business questions with SQL, and produces charts and summary tables that can be used in Power BI.

> **Dataset note:** `data/raw/sales.csv` is a synthetic dataset created for this portfolio project. It is not real company data, and the findings are demonstrations of the analysis workflow rather than claims about an actual business.

## Projects in this repository

### 1. Sales Performance & Business Intelligence

A retail sales workflow using Python, SQL, SQLite, Streamlit and Power BI guidance. It validates order data, calculates revenue and profit, and generates dashboard-ready summaries.

- [Run instructions and analysis details](README.md)

### 2. Customer Churn Prediction

A classification project comparing logistic regression with random forest on a synthetic customer dataset. It includes a stratified train/test split, preprocessing pipelines, precision, recall, F1-score, ROC-AUC, confusion matrices, model-specific feature rankings, SQL summaries and an optional Streamlit dashboard.

- [Project README](projects/customer-churn-prediction/README.md)
- [Analysis script](projects/customer-churn-prediction/scripts/run_analysis.py)
- [SQL queries](projects/customer-churn-prediction/sql/churn_analysis.sql)

Both projects use synthetic portfolio data. Do not treat their results as findings about a real company.

## Business questions

- Which months generate the most revenue and profit?
- Which regions and product categories contribute most to profit?
- How do discounts relate to profit margin?
- Which sales channels and customer segments account for the largest share of sales?
- Where should a sales manager investigate performance further?

## Tools

Python, pandas, Matplotlib, SQLite, SQL, Streamlit (optional interactive dashboard), Power BI.

## Repository layout

```text
Ai-and-Data-Analytics/
├── app.py
├── data/
│   ├── README.md
│   └── raw/sales.csv
├── docs/POWER_BI_GUIDE.md
├── reports/                 # generated charts and findings
├── scripts/run_analysis.py
├── sql/analysis.sql
├── tests/test_analysis.py
├── requirements.txt
└── .github/workflows/quality-check.yml
```

## Run it locally

Use Python 3.10 or newer. From the repository root:

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/run_analysis.py
python -m unittest discover -s tests -v
```

If PowerShell blocks activation, run the commands using `.\.venv\Scripts\python.exe` instead of activating the environment.

### Linux / macOS / WSL

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/run_analysis.py
python -m unittest discover -s tests -v
```

The analysis script writes the following files:

- `outputs/sales_enriched.csv` — validated order-level data with revenue, cost, profit, and margin.
- `outputs/monthly_summary.csv`, `outputs/region_summary.csv`, `outputs/category_summary.csv`, `outputs/channel_summary.csv` — tables for analysis and dashboards.
- `outputs/sales_analysis.db` — SQLite database with the enriched `sales` table.
- `reports/monthly_revenue.png` and `reports/profit_by_region.png` — generated charts.
- `reports/key_findings.md` — findings calculated from the current input data.

The generated files are intentionally not committed; run the script to reproduce them from the source CSV.

## Optional interactive dashboard

After running the analysis script:

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit. The app reads the generated summary tables and lets you filter by region and category.

## SQL analysis

The Python script creates `outputs/sales_analysis.db`. Open it with SQLite and run the queries in `sql/analysis.sql`. For example:

```bash
sqlite3 outputs/sales_analysis.db
```

If the `sqlite3` command-line tool is not installed, use DB Browser for SQLite or the Python standard library.

## Power BI

Follow [the Power BI guide](docs/POWER_BI_GUIDE.md) to load the enriched CSV, create measures, and build a report. A Power BI `.pbix` file is not included; create it in Power BI Desktop using the generated data.

## How the calculations work

- **Gross sales** = quantity × unit price
- **Revenue** = gross sales × (1 − discount percentage)
- **Cost** = quantity × unit cost
- **Profit** = revenue − cost
- **Profit margin** = profit ÷ revenue, where revenue is non-zero

Revenue is net of the row-level discount. Taxes, shipping, returns, and inventory costs are not modelled. Negative profit is allowed and should not be removed from the analysis.

## Quality and interpretation

The workflow runs the analysis and unit tests on pushes and pull requests. Since the data is synthetic, use the results to demonstrate the process and code quality—not as evidence of real market behaviour. For a real business dataset, record its source and licence before publishing it.

## Licence

MIT. See [LICENSE](LICENSE).
