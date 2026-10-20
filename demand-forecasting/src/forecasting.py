"""Monthly demand forecasting with chronological evaluation."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

DATE_COL = "date"
TARGET_COL = "units_sold"
FEATURE_COLS = ["month", "quarter", "year", "time_index", "lag_1", "lag_2", "lag_3", "lag_12", "rolling_mean_3"]

def load_sales(path: str | Path) -> pd.DataFrame:
    """Load and validate a date-indexed monthly sales table."""
    df = pd.read_csv(path, parse_dates=[DATE_COL]).sort_values(DATE_COL).reset_index(drop=True)
    missing = {DATE_COL, TARGET_COL}.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df[DATE_COL].isna().any() or df[TARGET_COL].isna().any():
        raise ValueError("Dates and sales values must not be missing.")
    if df[DATE_COL].duplicated().any():
        raise ValueError("Each month must appear only once.")
    if (df[TARGET_COL] < 0).any():
        raise ValueError("Sales values cannot be negative.")
    df[DATE_COL] = df[DATE_COL].dt.to_period("M").dt.to_timestamp()
    return df

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build calendar, lag and rolling features without looking forward."""
    out = df.copy().sort_values(DATE_COL).reset_index(drop=True)
    out["month"] = out[DATE_COL].dt.month
    out["quarter"] = out[DATE_COL].dt.quarter
    out["year"] = out[DATE_COL].dt.year
    out["time_index"] = np.arange(len(out), dtype=int)
    for lag in (1, 2, 3, 12):
        out[f"lag_{lag}"] = out[TARGET_COL].shift(lag)
    out["rolling_mean_3"] = out[TARGET_COL].shift(1).rolling(3).mean()
    return out

def chronological_split(df: pd.DataFrame, test_months: int = 6):
    """Return train and test frames in time order, keeping test months last."""
    if test_months < 1 or test_months >= len(df):
        raise ValueError("test_months must be at least 1 and smaller than row count.")
    return df.iloc[:-test_months].copy(), df.iloc[-test_months:].copy()

def evaluate_forecast(actual, predicted) -> dict[str, float]:
    """Compute MAE, RMSE and MAPE; MAPE excludes zero actual values."""
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    mae = mean_absolute_error(actual, predicted)
    rmse = float(np.sqrt(mean_squared_error(actual, predicted)))
    nonzero = actual != 0
    mape = float(np.mean(np.abs((actual[nonzero] - predicted[nonzero]) / actual[nonzero])) * 100) if nonzero.any() else float("nan")
    return {"mae": float(mae), "rmse": rmse, "mape_percent": mape}

def seasonal_naive(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    """Baseline forecast: use the value from the same month one year earlier."""
    history = train.set_index(DATE_COL)[TARGET_COL].to_dict()
    predictions = []
    for _, row in test.iterrows():
        prior_year = row[DATE_COL] - pd.DateOffset(months=12)
        predictions.append(float(history[prior_year]) if prior_year in history else float(train[TARGET_COL].iloc[-1]))
    return np.asarray(predictions)

def fit_and_evaluate(df: pd.DataFrame, test_months: int = 6):
    """Fit on the training period and compare against a seasonal-naive baseline."""
    featured = add_features(df).dropna().reset_index(drop=True)
    train, test = chronological_split(featured, test_months)
    model = RandomForestRegressor(n_estimators=300, max_depth=8, min_samples_leaf=2, random_state=42, n_jobs=-1)
    model.fit(train[FEATURE_COLS], train[TARGET_COL])
    model_pred = model.predict(test[FEATURE_COLS])
    baseline_pred = seasonal_naive(train, test)
    metrics = {
        "random_forest": evaluate_forecast(test[TARGET_COL], model_pred),
        "seasonal_naive": evaluate_forecast(test[TARGET_COL], baseline_pred),
    }
    results = pd.DataFrame({
        "date": test[DATE_COL].values,
        "actual": test[TARGET_COL].values,
        "random_forest_forecast": model_pred,
        "seasonal_naive_forecast": baseline_pred,
    })
    return model, metrics, results, featured

def forecast_future(df: pd.DataFrame, periods: int = 6) -> pd.DataFrame:
    """Refit on all observed data and recursively forecast future months."""
    if periods < 1:
        raise ValueError("periods must be positive.")
    featured = add_features(df).dropna().reset_index(drop=True)
    model = RandomForestRegressor(n_estimators=300, max_depth=8, min_samples_leaf=2, random_state=42, n_jobs=-1)
    model.fit(featured[FEATURE_COLS], featured[TARGET_COL])
    history = df[["date", TARGET_COL]].copy().sort_values("date").reset_index(drop=True)
    rows = []
    for _ in range(periods):
        next_date = history["date"].iloc[-1] + pd.DateOffset(months=1)
        values = history[TARGET_COL]
        feature_row = {
            "month": next_date.month, "quarter": next_date.quarter, "year": next_date.year,
            "time_index": len(history), "lag_1": float(values.iloc[-1]),
            "lag_2": float(values.iloc[-2]), "lag_3": float(values.iloc[-3]),
            "lag_12": float(values.iloc[-12]) if len(values) >= 12 else float(values.iloc[-1]),
            "rolling_mean_3": float(values.tail(3).mean()),
        }
        prediction = max(0.0, float(model.predict(pd.DataFrame([feature_row], columns=FEATURE_COLS))[0]))
        rows.append({"date": next_date, "forecast_units": prediction})
        history = pd.concat([history, pd.DataFrame([{"date": next_date, TARGET_COL: prediction}])], ignore_index=True)
    return pd.DataFrame(rows)
