# Demand Forecasting & Sales Prediction

A reproducible time-series project that compares a Random Forest regression model with a seasonal-naive baseline, evaluates both on a chronological holdout period, and generates a six-month demand outlook.

## What it demonstrates

- Data validation and monthly time-series preparation.
- Calendar features, lag features and a trailing rolling mean.
- Time-ordered holdout evaluation rather than random train/test splitting.
- A transparent seasonal-naive baseline alongside a machine-learning model.
- MAE, RMSE and MAPE reporting, with MAPE calculated only for non-zero actuals.
- Exported CSV results, a forecast chart, unit tests and a Streamlit dashboard.

## Data

The included data/monthly_sales.csv contains synthetic monthly unit sales for one illustrative retail product. It is not real company data. Replace it with permitted business data before drawing operational conclusions.

Expected CSV columns:

    date,units_sold

Use one row per month with non-negative unit sales. The dashboard accepts an uploaded CSV with the same columns.

## Run locally

From the repository root, install shared dependencies:

    python -m pip install -r requirements.txt

Run the analysis:

    python demand-forecasting/scripts/run_analysis.py

Run tests:

    python -m unittest discover -s demand-forecasting/tests -v

Launch the dashboard:

    streamlit run demand-forecasting/app.py

The analysis writes reproducible files under outputs/ and a chart under figures/. Generated outputs are intentionally not committed.

## Methodology

The last six feature-ready months are held out for evaluation by default. Training observations precede the holdout chronologically. The Random Forest uses calendar, lagged demand and rolling-mean features. The baseline predicts each holdout month using the value from twelve months earlier when available.

The forward forecast refits on all available history and predicts one month at a time, updating lag features with each prediction. This recursive approach can compound errors over longer horizons.

## Metrics

- **MAE:** average absolute error in units; easy to interpret in business terms.
- **RMSE:** penalizes larger errors more heavily than MAE.
- **MAPE:** mean absolute percentage error, excluding zero actuals.

Compare the machine-learning model with the baseline. A more complex model is not automatically better; if the baseline performs better, report that result honestly.

## Limitations

- The dataset is synthetic, small and intentionally simple.
- There is one aggregate series, with no product, store, promotion, price, stockout or holiday covariates.
- Random Forest is not inherently a time-series model; performance depends on feature design and historical coverage.
- The holdout covers only a short period. Use rolling-origin backtesting and prediction intervals for a production assessment.
- Forecasts are decision support, not guarantees. Check data quality, business context and inventory constraints before use.
