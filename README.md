# AI and Data Analytics Projects

This repository brings together practical projects in business intelligence, predictive modelling and applied AI. Each project has its own folder with the analysis code, data notes, documentation and instructions needed to reproduce the work.

## Projects

| Project | Focus | Tools |
|---|---|---|
| [Sales Performance & Business Intelligence](sales-performance-bi/) | Retail sales analysis, profitability measures, SQL summaries and dashboard-ready outputs | Python, pandas, SQLite, SQL, Streamlit, Power BI |
| [Customer Churn Prediction](customer-churn-prediction/) | Compare classification models with a held-out test set and review churn patterns | Python, scikit-learn, pandas, SQL, Matplotlib, Streamlit |
| [AI Research Assistant (RAG)](ai-research-assistant-rag/) | Search local documents, retrieve relevant passages and answer with source citations | Python, scikit-learn, TF-IDF, Streamlit, optional OpenAI API |
| [Demand Forecasting & Sales Prediction](demand-forecasting/) | Compare time-series baseline and machine-learning forecasts; evaluate holdout accuracy | Python, pandas, scikit-learn, Matplotlib, Streamlit |
| [Clinical Data Analytics — Power BI & Tableau](clinical-data-analytics/) | Clinical operations, simulated outcomes, lab summaries and BI dashboard design | Power BI, DAX, Power Query, Tableau, Python, pandas |

The sales, churn, demand-forecasting and clinical analytics projects use synthetic datasets. The clinical project is strictly a BI portfolio demonstration, not real patient data or clinical decision support. The RAG assistant includes original demonstration notes; add your own permitted TXT, Markdown or PDF documents to research your own material. The assistant does not browse the internet.

## Repository structure

```text
Ai-and-Data-Analytics/
├── sales-performance-bi/       # Business intelligence project
├── customer-churn-prediction/   # Machine learning project
├── ai-research-assistant-rag/    # Retrieval-augmented document assistant
├── demand-forecasting/           # Time-series forecasting project
├── clinical-data-analytics/      # Power BI and Tableau clinical analytics
├── docs/                        # Repository-wide documentation
├── .github/workflows/           # Automated checks
├── LICENSE
├── README.md
├── requirements.txt
└── .gitignore
```

Each project folder contains its own README, data, scripts, SQL, tests and relevant figures. Shared Python dependencies are listed in the root `requirements.txt`; generated outputs are kept out of version control and can be recreated by running the analysis scripts.

## Setup

Use Python 3.10 or newer. From the repository root:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux, macOS or WSL:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Follow the run instructions in the README inside each project. GitHub Actions runs analysis and unit tests for all five projects on pushes and pull requests.

## Documentation

- [Repository structure and contribution notes](docs/REPOSITORY_STRUCTURE.md)
- [Sales Performance & Business Intelligence](sales-performance-bi/README.md)
- [Customer Churn Prediction](customer-churn-prediction/README.md)
- [AI Research Assistant (RAG)](ai-research-assistant-rag/README.md)
- [Demand Forecasting & Sales Prediction](demand-forecasting/README.md)
- [Clinical Data Analytics — Power BI & Tableau](clinical-data-analytics/README.md)

## Licence

Code and documentation are released under the [MIT License](LICENSE), unless a file states otherwise. External datasets, libraries and other third-party materials remain subject to their own licences and terms.
