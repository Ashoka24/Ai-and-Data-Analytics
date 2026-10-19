import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
from run_analysis import load_data, run_analysis


class ChurnAnalysisTests(unittest.TestCase):
    def test_dataset_is_valid_and_target_is_binary(self):
        df = load_data()
        self.assertGreaterEqual(len(df), 500)
        self.assertEqual(set(df["churn"].unique()), {"Yes", "No"})
        self.assertTrue(df["customer_id"].is_unique)

    def test_analysis_writes_metrics_for_both_models(self):
        source = Path(__file__).resolve().parents[1] / "data" / "customer_churn.csv"
        with tempfile.TemporaryDirectory() as tmp:
            metrics = run_analysis(source, Path(tmp))
            self.assertEqual(set(metrics["model"]), {"logistic_regression", "random_forest"})
            self.assertTrue(metrics["roc_auc"].between(0, 1).all())
            self.assertTrue((Path(tmp) / "roc_curves.png").exists())
            self.assertTrue((Path(tmp) / "key_findings.md").exists())

    def test_missing_required_columns_raise_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.csv"
            pd.DataFrame({"customer_id": ["C1"], "churn": ["No"]}).to_csv(bad, index=False)
            with self.assertRaises(ValueError):
                load_data(bad)


if __name__ == "__main__":
    unittest.main()
