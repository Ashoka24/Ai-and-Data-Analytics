import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.run_analysis import build_summaries, load_sales


class SalesAnalysisTests(unittest.TestCase):
    def test_revenue_cost_profit_and_margin(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sales.csv"
            pd.DataFrame([{
                "order_id": "ORD1", "order_date": "2025-01-01",
                "region": "South", "state": "Karnataka", "category": "Electronics",
                "product": "Mouse", "quantity": 2, "unit_price": 100,
                "unit_cost": 40, "discount_pct": 0.10, "channel": "Online",
                "customer_segment": "Consumer",
            }]).to_csv(path, index=False)
            result = load_sales(path)
            self.assertAlmostEqual(result.loc[0, "gross_sales"], 200)
            self.assertAlmostEqual(result.loc[0, "revenue"], 180)
            self.assertAlmostEqual(result.loc[0, "cost"], 80)
            self.assertAlmostEqual(result.loc[0, "profit"], 100)
            self.assertAlmostEqual(result.loc[0, "profit_margin"], 100 / 180)

    def test_summary_totals_match_source(self):
        df = load_sales()
        summaries = build_summaries(df)
        self.assertEqual(int(summaries["monthly_summary"]["orders"].sum()), len(df))
        self.assertAlmostEqual(summaries["region_summary"]["revenue"].sum(), df["revenue"].sum())
        self.assertAlmostEqual(summaries["category_summary"]["profit"].sum(), df["profit"].sum())

    def test_invalid_discount_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sales.csv"
            pd.DataFrame([{
                "order_id": "ORD1", "order_date": "2025-01-01",
                "region": "South", "state": "Karnataka", "category": "Electronics",
                "product": "Mouse", "quantity": 2, "unit_price": 100,
                "unit_cost": 40, "discount_pct": 1.5, "channel": "Online",
                "customer_segment": "Consumer",
            }]).to_csv(path, index=False)
            with self.assertRaises(ValueError):
                load_sales(path)


if __name__ == "__main__":
    unittest.main()
