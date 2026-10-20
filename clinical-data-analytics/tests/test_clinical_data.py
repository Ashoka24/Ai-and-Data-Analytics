import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from analyze_clinical_data import load_data, validate_data, build_summaries

class ClinicalDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.encounters, cls.labs = load_data()
    def test_encounter_ids_are_unique(self):
        self.assertEqual(len(self.encounters), self.encounters["EncounterID"].nunique())
    def test_lab_encounters_map_to_encounter_table(self):
        self.assertTrue(set(self.labs["EncounterID"]).issubset(set(self.encounters["EncounterID"])))
    def test_binary_flags_are_valid(self):
        self.assertTrue(set(self.encounters["ICUFlag"].unique()).issubset({0, 1}))
        self.assertTrue(set(self.encounters["SimulatedReadmissionFlag"].unique()).issubset({0, 1}))
    def test_abnormal_flag_matches_reference_ranges(self):
        expected = ((self.labs["Result"] < self.labs["ReferenceLow"]) | (self.labs["Result"] > self.labs["ReferenceHigh"])).astype(int)
        self.assertTrue(expected.equals(self.labs["AbnormalFlag"].astype(int)))
    def test_validation_passes(self):
        self.assertEqual(validate_data(self.encounters, self.labs), [])
    def test_summary_metrics_are_bounded(self):
        summary = build_summaries(self.encounters, self.labs)
        self.assertGreater(summary["encounters"], 0)
        self.assertGreater(summary["unique_patients"], 0)
        self.assertGreaterEqual(summary["readmission_30d_rate_pct"], 0)
        self.assertLessEqual(summary["readmission_30d_rate_pct"], 100)
        self.assertGreaterEqual(summary["lab_abnormal_rate_pct"], 0)
        self.assertLessEqual(summary["lab_abnormal_rate_pct"], 100)
if __name__ == "__main__":
    unittest.main()
