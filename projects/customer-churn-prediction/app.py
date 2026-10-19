from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "customer_churn.csv"
OUT = ROOT / "outputs"

st.set_page_config(page_title="Customer Churn", layout="wide")
st.title("Customer Churn Analysis")
st.caption("Synthetic portfolio dataset. Do not interpret these results as findings about a real provider.")

df = pd.read_csv(DATA)
region = st.selectbox("Contract type", ["All"] + sorted(df["contract"].unique().tolist()))
filtered = df if region == "All" else df[df["contract"] == region]
count = len(filtered)
churn_rate = (filtered["churn"] == "Yes").mean() if count else 0
avg_tenure = filtered["tenure_months"].mean() if count else 0
avg_monthly = filtered["monthly_charges"].mean() if count else 0
a,b,c,d = st.columns(4)
a.metric("Customers", f"{count:,}")
b.metric("Churn rate", f"{churn_rate:.1%}")
c.metric("Average tenure", f"{avg_tenure:.1f} months")
d.metric("Average monthly charge", f"{avg_monthly:.2f}")

left, right = st.columns(2)
with left:
    st.subheader("Churn by contract")
    chart = df.assign(churned=(df["churn"] == "Yes").astype(int)).groupby("contract")["churned"].mean()
    st.bar_chart(chart)
with right:
    st.subheader("Churn by tenure")
    tenure = df.assign(tenure_band=pd.cut(df["tenure_months"], [0,6,12,24,48,73], labels=["0–5","6–11","12–23","24–47","48–72"]))
    st.bar_chart(tenure.groupby("tenure_band", observed=False)["churn"].apply(lambda s: (s == "Yes").mean()))

if (OUT / "model_metrics.csv").exists():
    st.subheader("Held-out model comparison")
    st.dataframe(pd.read_csv(OUT / "model_metrics.csv"), use_container_width=True, hide_index=True)
    if (OUT / "roc_curves.png").exists():
        st.image(str(OUT / "roc_curves.png"), caption="ROC curves for the held-out test set")
else:
    st.info("Run scripts/run_analysis.py to generate model evaluation outputs.")
