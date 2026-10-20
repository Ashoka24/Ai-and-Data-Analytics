"""Streamlit dashboard for the demand forecasting project."""
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from forecasting import fit_and_evaluate, forecast_future, load_sales

st.set_page_config(page_title="Demand Forecasting", page_icon="📈", layout="wide")
st.title("Demand Forecasting & Sales Prediction")
st.caption("Monthly retail demand | chronological holdout evaluation | six-month outlook")
uploaded = st.sidebar.file_uploader("Optional monthly sales CSV", type=["csv"])
if uploaded is not None:
    try:
        sales = pd.read_csv(uploaded, parse_dates=["date"])
        temp_path = ROOT / "outputs" / "_uploaded_sales_temp.csv"
        temp_path.parent.mkdir(exist_ok=True)
        sales.to_csv(temp_path, index=False)
        sales = load_sales(temp_path)
        temp_path.unlink(missing_ok=True)
    except Exception as exc:
        st.error(f"Could not load the uploaded file: {exc}")
        st.stop()
else:
    sales = load_sales(ROOT / "data" / "monthly_sales.csv")
test_months = st.sidebar.slider("Holdout months", 3, 12, 6)
future_months = st.sidebar.slider("Forecast horizon (months)", 3, 12, 6)
if len(sales) < max(24, test_months + 15):
    st.warning("Use at least 24 monthly observations and enough history for lag features.")
    st.stop()
try:
    _, metrics, holdout, _ = fit_and_evaluate(sales, test_months=test_months)
    future = forecast_future(sales, periods=future_months)
except Exception as exc:
    st.error(f"Forecast could not be generated: {exc}")
    st.stop()
c1, c2, c3 = st.columns(3)
c1.metric("Months of history", f"{len(sales):,}")
c2.metric("Holdout MAE", f"{metrics['random_forest']['mae']:.1f} units")
c3.metric("Holdout RMSE", f"{metrics['random_forest']['rmse']:.1f} units")
st.subheader("Observed demand and forecast")
fig, ax = plt.subplots(figsize=(11, 4.8))
ax.plot(sales["date"], sales["units_sold"], label="Observed sales", linewidth=2)
ax.plot(pd.to_datetime(holdout["date"]), holdout["random_forest_forecast"], label="Random Forest holdout", marker="o")
ax.plot(pd.to_datetime(holdout["date"]), holdout["seasonal_naive_forecast"], label="Seasonal-naive baseline", linestyle="--", marker=".")
ax.plot(future["date"], future["forecast_units"], label="Future forecast", linestyle=":", marker="o")
ax.axvline(sales["date"].max(), linestyle="--", linewidth=1)
ax.set_xlabel("Month")
ax.set_ylabel("Units sold")
ax.grid(alpha=0.25)
ax.legend()
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)
st.subheader("Model comparison on the holdout period")
comparison = pd.DataFrame(metrics).T.rename(columns={"mae": "MAE (units)", "rmse": "RMSE (units)", "mape_percent": "MAPE (%)"})
st.dataframe(comparison.style.format("{:.2f}"), use_container_width=True)
winner = min(metrics, key=lambda name: metrics[name]["mae"])
st.write(f"Lower holdout MAE in this run: **{winner.replace('_', ' ').title()}**. This is a test-period comparison, not a guarantee of future performance.")
left, right = st.columns(2)
with left:
    st.subheader("Holdout predictions")
    st.dataframe(holdout.round(2), use_container_width=True, hide_index=True)
with right:
    st.subheader("Forward forecast")
    st.dataframe(future.round(2), use_container_width=True, hide_index=True)
st.download_button("Download future forecast CSV", future.to_csv(index=False).encode("utf-8"), "future_forecast.csv", "text/csv")
st.info("The bundled data are synthetic and intended for demonstration. Validate forecasts on representative business data before using them for inventory or purchasing decisions.")
