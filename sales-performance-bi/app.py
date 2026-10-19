from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"

st.set_page_config(page_title="Sales Performance", layout="wide")
st.title("Sales Performance Dashboard")
st.caption("Portfolio demonstration using a synthetic retail dataset. Run the project analysis script before launching.")

required = [OUT / "sales_enriched.csv", OUT / "monthly_summary.csv", OUT / "region_summary.csv", OUT / "category_summary.csv"]
if not all(p.exists() for p in required):
    st.warning("Analysis outputs are missing. From the repository root, run: python sales-performance-bi/scripts/run_analysis.py")
    st.stop()

sales = pd.read_csv(required[0], parse_dates=["order_date"])
regions = pd.read_csv(required[2])
categories = pd.read_csv(required[3])
months = pd.read_csv(required[1])

region_options = ["All"] + sorted(sales["region"].unique().tolist())
category_options = ["All"] + sorted(sales["category"].unique().tolist())
c1, c2 = st.columns(2)
with c1:
    region = st.selectbox("Region", region_options)
with c2:
    category = st.selectbox("Category", category_options)

filtered = sales.copy()
if region != "All":
    filtered = filtered[filtered["region"] == region]
if category != "All":
    filtered = filtered[filtered["category"] == category]

revenue = filtered["revenue"].sum()
profit = filtered["profit"].sum()
margin = profit / revenue if revenue else 0
m1, m2, m3, m4 = st.columns(4)
m1.metric("Orders", f"{filtered['order_id'].nunique():,}")
m2.metric("Net revenue", f"{revenue:,.0f}")
m3.metric("Profit", f"{profit:,.0f}")
m4.metric("Profit margin", f"{margin:.1%}")

left, right = st.columns(2)
with left:
    monthly = filtered.groupby("month", as_index=False)["revenue"].sum().sort_values("month")
    st.subheader("Monthly net revenue")
    st.line_chart(monthly.set_index("month")["revenue"])
with right:
    region_summary = filtered.groupby("region", as_index=False)["profit"].sum().sort_values("profit")
    st.subheader("Profit by region")
    st.bar_chart(region_summary.set_index("region")["profit"])

st.subheader("Product performance")
product_summary = (filtered.groupby(["category", "product"], as_index=False)
                   .agg(units=("quantity", "sum"), revenue=("revenue", "sum"), profit=("profit", "sum"))
                   .sort_values("profit", ascending=False))
st.dataframe(product_summary, use_container_width=True, hide_index=True)
st.download_button("Download filtered data", filtered.to_csv(index=False).encode("utf-8"),
                   file_name="filtered_sales.csv", mime="text/csv")
