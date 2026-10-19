from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "sales.csv"
OUTPUT = ROOT / "outputs"
REPORTS = ROOT / "reports"

REQUIRED_COLUMNS = {
    "order_id", "order_date", "region", "state", "category", "product",
    "quantity", "unit_price", "unit_cost", "discount_pct", "channel",
    "customer_segment",
}


def load_sales(path: Path = INPUT) -> pd.DataFrame:
    """Read the source CSV and validate fields needed by the analysis."""
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if df.empty:
        raise ValueError("The input dataset contains no rows.")
    if df["order_id"].isna().any() or df["order_id"].duplicated().any():
        raise ValueError("order_id values must be present and unique.")

    df["order_date"] = pd.to_datetime(df["order_date"], errors="raise")
    for col in ("quantity", "unit_price", "unit_cost", "discount_pct"):
        df[col] = pd.to_numeric(df[col], errors="raise")
    if (df["quantity"] <= 0).any():
        raise ValueError("quantity must be greater than zero.")
    if (df[["unit_price", "unit_cost"]] < 0).any().any():
        raise ValueError("unit_price and unit_cost cannot be negative.")
    if not df["discount_pct"].between(0, 1).all():
        raise ValueError("discount_pct must be between 0 and 1.")
    if df[list(REQUIRED_COLUMNS)].isna().any().any():
        raise ValueError("Required fields cannot contain missing values.")

    df["gross_sales"] = df["quantity"] * df["unit_price"]
    df["revenue"] = df["gross_sales"] * (1 - df["discount_pct"])
    df["cost"] = df["quantity"] * df["unit_cost"]
    df["profit"] = df["revenue"] - df["cost"]
    df["profit_margin"] = df["profit"].div(df["revenue"].where(df["revenue"] != 0))
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    return df.sort_values(["order_date", "order_id"]).reset_index(drop=True)


def build_summaries(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    monthly = (
        df.groupby("month", as_index=False)
        .agg(orders=("order_id", "nunique"), units=("quantity", "sum"),
             revenue=("revenue", "sum"), profit=("profit", "sum"))
        .sort_values("month")
    )
    monthly["profit_margin"] = monthly["profit"] / monthly["revenue"].replace(0, pd.NA)

    region = (
        df.groupby("region", as_index=False)
        .agg(orders=("order_id", "nunique"), revenue=("revenue", "sum"),
             profit=("profit", "sum"), units=("quantity", "sum"))
        .sort_values("revenue", ascending=False)
    )
    region["profit_margin"] = region["profit"] / region["revenue"].replace(0, pd.NA)

    category = (
        df.groupby("category", as_index=False)
        .agg(orders=("order_id", "nunique"), revenue=("revenue", "sum"),
             profit=("profit", "sum"), units=("quantity", "sum"))
        .sort_values("revenue", ascending=False)
    )
    category["profit_margin"] = category["profit"] / category["revenue"].replace(0, pd.NA)

    channel = (
        df.groupby(["channel", "customer_segment"], as_index=False)
        .agg(orders=("order_id", "nunique"), revenue=("revenue", "sum"),
             profit=("profit", "sum"))
        .sort_values("revenue", ascending=False)
    )
    return {
        "monthly_summary": monthly,
        "region_summary": region,
        "category_summary": category,
        "channel_summary": channel,
    }


def write_database(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        df.to_sql("sales", connection, if_exists="replace", index=False)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(order_date)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_sales_region ON sales(region)")


def write_charts(summaries: dict[str, pd.DataFrame]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    monthly = summaries["monthly_summary"]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly["month"], monthly["revenue"], marker="o", linewidth=2)
    ax.set_title("Monthly Net Revenue")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue")
    ax.tick_params(axis="x", rotation=55)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(REPORTS / "monthly_revenue.png", dpi=160)
    plt.close(fig)

    region = summaries["region_summary"].sort_values("profit", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(region["region"], region["profit"])
    ax.set_title("Profit by Region")
    ax.set_xlabel("Profit")
    ax.set_ylabel("Region")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(REPORTS / "profit_by_region.png", dpi=160)
    plt.close(fig)


def write_findings(df: pd.DataFrame, summaries: dict[str, pd.DataFrame]) -> None:
    revenue = float(df["revenue"].sum())
    profit = float(df["profit"].sum())
    margin = profit / revenue if revenue else 0.0
    best_region = summaries["region_summary"].sort_values("profit", ascending=False).iloc[0]
    best_category = summaries["category_summary"].sort_values("profit", ascending=False).iloc[0]
    best_month = summaries["monthly_summary"].sort_values("revenue", ascending=False).iloc[0]
    content = f"""# Key findings

These figures are calculated from the current input file. The dataset is synthetic and is used only to demonstrate the workflow.

- **Orders analysed:** {df['order_id'].nunique():,}
- **Net revenue:** {revenue:,.2f}
- **Profit:** {profit:,.2f}
- **Overall profit margin:** {margin:.1%}
- **Highest-profit region:** {best_region['region']} (profit {best_region['profit']:,.2f})
- **Highest-profit category:** {best_category['category']} (profit {best_category['profit']:,.2f})
- **Highest-revenue month:** {best_month['month']} (revenue {best_month['revenue']:,.2f})

## Follow-up questions

1. Are high-revenue products also generating healthy profit margins?
2. Do larger discounts consistently correspond to lower profit?
3. Are results stable across regions and customer segments?
4. What changes when results are grouped by month rather than order date?

These are descriptive findings, not causal conclusions. Validate any business decision with real, appropriately licensed data.
"""
    (REPORTS / "key_findings.md").write_text(content, encoding="utf-8")


def run(input_path: Path = INPUT) -> dict[str, object]:
    df = load_sales(input_path)
    summaries = build_summaries(df)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT / "sales_enriched.csv", index=False, float_format="%.4f")
    for name, table in summaries.items():
        table.to_csv(OUTPUT / f"{name}.csv", index=False, float_format="%.4f")
    write_database(df, OUTPUT / "sales_analysis.db")
    write_charts(summaries)
    write_findings(df, summaries)
    return {
        "orders": int(df["order_id"].nunique()),
        "revenue": round(float(df["revenue"].sum()), 2),
        "profit": round(float(df["profit"].sum()), 2),
        "outputs": str(OUTPUT),
    }


if __name__ == "__main__":
    result = run()
    print("Sales analysis completed.")
    for key, value in result.items():
        print(f"{key}: {value}")
    print(f"Charts and findings: {REPORTS}")
