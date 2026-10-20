import sys
import unittest
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from forecasting import add_features, chronological_split, evaluate_forecast, fit_and_evaluate, forecast_future, load_sales

class ForecastingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_sales(ROOT / "data" / "monthly_sales.csv")

    def test_dataset_has_unique_months_and_nonnegative_sales(self):
        self.assertEqual(len(self.data), self.data["date"].nunique())
        self.assertTrue((self.data["units_sold"] >= 0).all())
        self.assertGreaterEqual(len(self.data), 36)

    def test_lag_features_use_past_values(self):
        featured = add_features(self.data)
        self.assertTrue(featured.loc[12:, "lag_12"].notna().all())
        self.assertEqual(featured.loc[12, "lag_12"], self.data.loc[0, "units_sold"])

    def test_split_preserves_time_order(self):
        train, test = chronological_split(self.data, test_months=6)
        self.assertLess(train["date"].max(), test["date"].min())
        self.assertEqual(len(test), 6)

    def test_metrics_are_nonnegative(self):
        metrics = evaluate_forecast([10, 20, 30], [12, 18, 33])
        self.assertGreaterEqual(metrics["mae"], 0)
        self.assertGreaterEqual(metrics["rmse"], 0)
        self.assertGreaterEqual(metrics["mape_percent"], 0)

    def test_models_return_holdout_predictions(self):
        _, metrics, results, _ = fit_and_evaluate(self.data, test_months=6)
        self.assertEqual(len(results), 6)
        self.assertEqual(set(metrics), {"random_forest", "seasonal_naive"})
        self.assertTrue(np.isfinite(results["random_forest_forecast"]).all())

    def test_future_forecast_has_six_months_after_history(self):
        future = forecast_future(self.data, periods=6)
        self.assertEqual(len(future), 6)
        self.assertGreater(future["date"].min(), self.data["date"].max())
        self.assertTrue((future["forecast_units"] >= 0).all())

if __name__ == "__main__":
    unittest.main()
