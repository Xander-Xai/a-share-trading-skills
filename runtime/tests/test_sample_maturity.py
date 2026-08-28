import unittest

from runtime.sample_maturity import classify_maturity, summarize


class SampleMaturityTests(unittest.TestCase):
    def test_early_accumulation(self):
        records = [
            {
                "record_key": f"s1:2026-08-0{i}",
                "sample_id": "s1",
                "sample_role": "RETROSPECTIVE_LIVE_MANUAL",
                "code": "600699",
                "name": "均胜电子",
                "effective_date": f"2026-08-0{i}",
                "data_quality": {
                    "price_complete": True,
                    "market_complete": True,
                    "benchmark_complete": True,
                    "participation_complete": True,
                    "financing_complete_or_not_applicable": True,
                    "disclosure_scan_complete": True,
                    "manual_execution_complete": True,
                },
            }
            for i in range(1, 4)
        ]
        result = summarize(records)
        self.assertEqual(result["sample_count"], 1)
        self.assertEqual(result["samples"][0]["data_maturity"], "EARLY_ACCUMULATION")

    def test_mature_requires_core_coverage(self):
        coverage = {
            "price_complete_pct": 100.0,
            "market_complete_pct": 100.0,
            "benchmark_complete_pct": 100.0,
            "disclosure_scan_complete_pct": 100.0,
        }
        self.assertEqual(classify_maturity(15, coverage), "OPERATIONALLY_MATURE_FOR_FEATURE_RESEARCH")
        coverage["benchmark_complete_pct"] = 80.0
        self.assertEqual(classify_maturity(15, coverage), "COVERAGE_GAPS")


if __name__ == "__main__":
    unittest.main()
