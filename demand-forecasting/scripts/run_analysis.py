"""Run the demand forecasting analysis and write reproducible outputs."""
from pathlib import Path
import json
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from forecasting import fit_and_evaluate, forecast_future, load_sales

def main() -> None:
    sales = load_sales(ROOT / "data" / "monthly_sales.csv")
    output_dir, figures_dir = ROOT / "outputs", ROOT / "figures"
    output_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)
    _, metrics, holdout, _ = fit_and_evaluate(sales, test_months=6)
    future = forecast_future(sales, periods=6)
    holdout.to_csv(output_dir / "holdout_forecasts.csv", index=False, float_format="%.2f")
    future.to_csv(output_dir / "future_forecast.csv", index=False, float_format="%.2f")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(sales["date"], sales["units_sold"], label="Observed sales", linewidth=2)
    ax.plot(pd.to_datetime(holdout["date"]), holdout["random_forest_forecast"], label="Random Forest holdout", marker="o")
    ax.plot(pd.to_datetime(holdout["date"]), holdout["seasonal_naive_forecast"], label="Seasonal-naive baseline", linestyle="--", marker=".")
    ax.plot(future["date"], future["forecast_units"], label="Next 6 months", marker="o", linestyle=":")
    ax.axvline(sales["date"].max(), linestyle="--", linewidth=1, label="Forecast starts")
    ax.set(title="Monthly demand: actuals and forecasts", xlabel="Month", ylabel="Units sold")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures_dir / "demand_forecast.png", dpi=160)
    plt.close(fig)
    print("Demand forecasting analysis complete.")
    print(json.dumps(metrics, indent=2))
    print(f"Holdout forecasts: {output_dir / 'holdout_forecasts.csv'}")
    print(f"Future forecasts:  {output_dir / 'future_forecast.csv'}")
    print(f"Chart:             {figures_dir / 'demand_forecast.png'}")

if __name__ == "__main__":
    main()
