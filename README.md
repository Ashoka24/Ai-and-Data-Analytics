# AI and Data Analytics Projects

This repository brings together practical projects in business intelligence, predictive modelling, applied AI and data analysis. Each project has its own folder with code, data notes, documentation and reproducible instructions.

## Projects

| Project | Focus | Tools |
|---|---|---|
| [Sales Performance & Business Intelligence](sales-performance-bi/) | Retail sales analysis, profitability measures, SQL summaries and dashboard-ready outputs | Python, pandas, SQLite, SQL, Streamlit, Power BI |
| [Customer Churn Prediction](customer-churn-prediction/) | Compare classification models with a held-out test set and review churn patterns | Python, scikit-learn, pandas, SQL, Matplotlib, Streamlit |
| [AI Research Assistant (RAG)](ai-research-assistant-rag/) | Search local documents, retrieve relevant passages and answer with source citations | Python, scikit-learn, TF-IDF, Streamlit, optional OpenAI API |
| [Demand Forecasting & Sales Prediction](demand-forecasting/) | Compare time-series baseline and machine-learning forecasts; evaluate holdout accuracy | Python, pandas, scikit-learn, Matplotlib, Streamlit |
| [Clinical Data Analysis](clinical-data-analytics/) | Clinical cohort profiling, data-quality checks, lab-result analysis and exploratory statistics | Python, pandas, SciPy, Matplotlib |

The sales, churn, demand-forecasting and clinical projects use synthetic data. Clinical analysis outputs are demonstrations only—not real patient findings or clinical decision support. The RAG assistant uses demonstration notes; add your own permitted TXT, Markdown or PDF documents to research your own material. The assistant does not browse the internet.

## Repository structure

```text
Ai-and-Data-Analytics/
├── sales-performance-bi/
├── customer-churn-prediction/
├── ai-research-assistant-rag/
├── demand-forecasting/
├── clinical-data-analytics/      # Clinical data analysis in Python
├── docs/
├── .github/workflows/
├── LICENSE
├── README.md
├── requirements.txt
└── .gitignore
```

Each project folder contains its own README, data, scripts, tests and relevant documentation. Shared Python dependencies are listed in the root `requirements.txt`; generated outputs can be recreated by running each project's analysis script.

## Setup

Use Python 3.10 or newer. From the repository root:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

Linux, macOS or WSL:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Follow the run instructions in each project README. GitHub Actions runs analysis and unit tests for the repository projects on pushes and pull requests.

## Documentation

- [Repository structure and contribution notes](docs/REPOSITORY_STRUCTURE.md)
- [Sales Performance & Business Intelligence](sales-performance-bi/README.md)
- [Customer Churn Prediction](customer-churn-prediction/README.md)
- [AI Research Assistant (RAG)](ai-research-assistant-rag/README.md)
- [Demand Forecasting & Sales Prediction](demand-forecasting/README.md)
- [Clinical Data Analysis](clinical-data-analytics/README.md)
- [Clinical evidence and data validity audit](clinical-data-analytics/docs/clinical-evidence-and-data-audit.md)

## Licence

Code and documentation are released under the [MIT License](LICENSE), unless a file states otherwise. External datasets, libraries and third-party materials remain subject to their own licences and terms.
