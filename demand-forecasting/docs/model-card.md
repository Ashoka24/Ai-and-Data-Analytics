# Model Card: Monthly Demand Forecast

## Intended use
Demonstrate a reproducible forecasting workflow for portfolio and educational purposes. It is not validated for operational purchasing, staffing or supply-chain decisions.

## Data
The repository includes synthetic monthly unit sales for a single illustrative product. The series is not representative of any specific company or market.

## Model
A scikit-learn Random Forest regressor uses month, quarter, year, time index, lagged unit sales and a trailing three-month mean. A seasonal-naive forecast is included as a benchmark.

## Evaluation
The default evaluation reserves the last six feature-ready observations as a chronological holdout. MAE, RMSE and MAPE are reported. MAPE excludes zero actuals. A single holdout can be unrepresentative, so production work should add rolling-origin backtesting.

## Risks and limitations
- Forecast quality depends on sufficient, accurate and relevant history.
- Promotions, holidays, price changes, stockouts and market shifts are not represented.
- Recursive multi-step forecasting may amplify errors.
- No prediction intervals are provided.
- Metrics from synthetic data must not be presented as evidence of real-world business performance.

## Recommended checks before real use
1. Confirm date granularity, missing periods, duplicate months and stockout handling.
2. Compare with seasonal-naive and business-rule baselines.
3. Evaluate across multiple time-based folds and relevant seasonal cycles.
4. Measure error by product, store and forecast horizon where possible.
5. Monitor drift and retrain only under a documented policy.
