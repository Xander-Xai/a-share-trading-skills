import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.core.pit import PITMetadata
from src.core.strategy_boundary import (
    LONG_SLEEVE,
    LONG_STRATEGY_ID,
    SHORT_MID_SLEEVE,
    SHORT_MID_STRATEGY_ID,
    require_strategy_context,
)


class StrategyBoundaryContractTests(unittest.TestCase):
    def test_matching_short_mid_context_passes(self):
        require_strategy_context(
            strategy_id=SHORT_MID_STRATEGY_ID,
            sleeve=SHORT_MID_SLEEVE,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )

    def test_long_context_rejected_by_short_mid_engine_contract(self):
        with self.assertRaises(ValueError):
            require_strategy_context(
                strategy_id=LONG_STRATEGY_ID,
                sleeve=LONG_SLEEVE,
                expected_strategy_id=SHORT_MID_STRATEGY_ID,
                expected_sleeve=SHORT_MID_SLEEVE,
            )


class PITMetadataTests(unittest.TestCase):
    def build_record(self, **overrides):
        data = {
            "record_id": "evt-1",
            "entity_type": "DISCLOSURE",
            "source": "exchange",
            "source_tier": "TIER1",
            "source_snapshot_id": "snap-1",
            "revision_id": "rev-1",
            "published_at": "2026-08-28T16:23:00+08:00",
            "available_at": "2026-08-28T16:23:05+08:00",
            "ingested_at": "2026-08-28T16:24:00+08:00",
            "strategy_visibility": ("long", "short_mid"),
            "permitted_use": "RESEARCH_ONLY",
        }
        data.update(overrides)
        return PITMetadata(**data)

    def test_valid_record_is_visible_after_available_at(self):
        record = self.build_record()
        record.validate()
        self.assertTrue(
            record.visible_to("short_mid", "2026-08-28T16:25:00+08:00")
        )

    def test_record_is_not_visible_before_available_at(self):
        record = self.build_record()
        self.assertFalse(
            record.visible_to("short_mid", "2026-08-28T16:22:59+08:00")
        )

    def test_available_at_cannot_precede_publication(self):
        record = self.build_record(
            available_at="2026-08-28T16:22:00+08:00"
        )
        with self.assertRaises(ValueError):
            record.validate()

    def test_strategy_visibility_is_enforced(self):
        record = self.build_record(strategy_visibility=("long",))
        self.assertFalse(
            record.visible_to("short_mid", "2026-08-28T16:25:00+08:00")
        )

    def test_timestamps_must_be_timezone_aware(self):
        record = self.build_record(available_at="2026-08-28T16:23:05")
        with self.assertRaises(ValueError):
            record.validate()


if __name__ == "__main__":
    unittest.main()
