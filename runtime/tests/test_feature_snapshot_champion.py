import json
import tempfile
import unittest
from pathlib import Path

from src.core.strategy_boundary import (
    LONG_SLEEVE,
    LONG_STRATEGY_ID,
    SHORT_MID_SLEEVE,
    SHORT_MID_STRATEGY_ID,
)
from src.features.snapshot import FeatureSnapshot, FeatureSnapshotStore, FeatureValue
from src.strategies.short_mid.champion import (
    ChampionInputError,
    ChampionScorer,
    load_champion_config,
)


CONFIG_PATH = Path("configs/short_mid/champion-v1.json")


class FeatureSnapshotChampionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_champion_config(CONFIG_PATH)
        cls.scorer = ChampionScorer(cls.config)

    def available(self, name, value):
        return FeatureValue(
            name=name,
            status="AVAILABLE",
            value=value,
            calculation_id="test-fixture-v1",
        )

    def build_features(
        self,
        *,
        regime="NEUTRAL",
        data_confidence="HIGH",
        penalty_overrides=None,
        score_overrides=None,
        veto_reasons=(),
        include_hard_veto_checked=True,
        omit_veto_flags=(),
    ):
        penalty_overrides = penalty_overrides or {}
        score_overrides = score_overrides or {}
        veto_reasons = set(veto_reasons)
        omit_veto_flags = set(omit_veto_flags)
        features = []

        unknown_vetoes = veto_reasons - set(self.config.hard_veto_flags)
        if unknown_vetoes:
            raise ValueError(f"unknown test veto flags: {sorted(unknown_vetoes)}")

        for section, criteria in self.config.base_sections.items():
            for criterion, cap in criteria.items():
                key = f"{section}.{criterion}"
                value = score_overrides.get(key, cap)
                features.append(
                    self.available(f"champion.{section}.{criterion}", value)
                )

        for name in self.config.penalty_caps:
            features.append(
                self.available(
                    f"champion.penalty.{name}",
                    penalty_overrides.get(name, 0),
                )
            )

        if include_hard_veto_checked:
            features.append(self.available("champion.hard_veto_checked", True))
        for flag in self.config.hard_veto_flags:
            if flag not in omit_veto_flags:
                features.append(
                    self.available(
                        f"champion.hard_veto.{flag}",
                        flag in veto_reasons,
                    )
                )

        features.extend(
            [
                self.available("champion.data_confidence", data_confidence),
                self.available("market.regime", regime),
            ]
        )
        return features

    def build_snapshot(
        self,
        *,
        strategy_id=SHORT_MID_STRATEGY_ID,
        sleeve=SHORT_MID_SLEEVE,
        data_snapshot_id="data-snapshot-001",
        regime="NEUTRAL",
        data_confidence="HIGH",
        penalty_overrides=None,
        score_overrides=None,
        veto_reasons=(),
        include_hard_veto_checked=True,
        omit_veto_flags=(),
    ):
        return FeatureSnapshot.build(
            strategy_id=strategy_id,
            sleeve=sleeve,
            as_of="2026-08-28T15:40:00+08:00",
            data_snapshot_id=data_snapshot_id,
            feature_set_version="short-mid-champion-feature-set-v0",
            implementation_version="feature-fixture-v1",
            config_version=self.config.config_version,
            features=self.build_features(
                regime=regime,
                data_confidence=data_confidence,
                penalty_overrides=penalty_overrides,
                score_overrides=score_overrides,
                veto_reasons=veto_reasons,
                include_hard_veto_checked=include_hard_veto_checked,
                omit_veto_flags=omit_veto_flags,
            ),
        )

    def test_config_freezes_expected_section_caps(self):
        self.assertEqual(
            self.config.section_caps,
            {
                "technical": 30.0,
                "capital": 30.0,
                "fundamentals": 25.0,
                "catalyst": 15.0,
            },
        )

    def test_feature_snapshot_is_deterministic_independent_of_feature_order(self):
        features = self.build_features()
        first = FeatureSnapshot.build(
            strategy_id=SHORT_MID_STRATEGY_ID,
            sleeve=SHORT_MID_SLEEVE,
            as_of="2026-08-28T15:40:00+08:00",
            data_snapshot_id="data-snapshot-001",
            feature_set_version="short-mid-champion-feature-set-v0",
            implementation_version="feature-fixture-v1",
            config_version=self.config.config_version,
            features=features,
        )
        second = FeatureSnapshot.build(
            strategy_id=SHORT_MID_STRATEGY_ID,
            sleeve=SHORT_MID_SLEEVE,
            as_of="2026-08-28T15:40:00+08:00",
            data_snapshot_id="data-snapshot-001",
            feature_set_version="short-mid-champion-feature-set-v0",
            implementation_version="feature-fixture-v1",
            config_version=self.config.config_version,
            features=reversed(features),
        )
        self.assertEqual(first.feature_snapshot_id, second.feature_snapshot_id)

    def test_data_snapshot_change_changes_feature_snapshot_identity(self):
        first = self.build_snapshot(data_snapshot_id="data-snapshot-001")
        second = self.build_snapshot(data_snapshot_id="data-snapshot-002")
        self.assertNotEqual(first.feature_snapshot_id, second.feature_snapshot_id)

    def test_feature_snapshot_manifest_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FeatureSnapshotStore(tmp)
            snapshot = store.save(self.build_snapshot())
            path = store.snapshots_dir / f"{snapshot.feature_snapshot_id}.json"
            row = json.loads(path.read_text(encoding="utf-8"))
            row["data_snapshot_id"] = "tampered"
            path.write_text(json.dumps(row), encoding="utf-8")
            with self.assertRaises(ValueError):
                store.load(snapshot.feature_snapshot_id)

    def test_max_score_is_100_and_never_authorizes_execution(self):
        result = self.scorer.score_feature_snapshot(self.build_snapshot())
        self.assertEqual(result.base_score, 100.0)
        self.assertEqual(result.final_score, 100.0)
        self.assertEqual(result.ranking_status, "HIGH_PRIORITY")
        self.assertTrue(result.score_threshold_passed)
        self.assertTrue(result.research_eligible)
        self.assertFalse(result.execution_authorized)

    def test_hard_veto_cannot_be_compensated_by_max_score(self):
        result = self.scorer.score_feature_snapshot(
            self.build_snapshot(veto_reasons=("data_completeness",))
        )
        self.assertEqual(result.final_score, 100.0)
        self.assertTrue(result.hard_veto)
        self.assertEqual(result.ranking_status, "REJECT_HARD_VETO")
        self.assertTrue(result.score_threshold_passed)
        self.assertFalse(result.research_eligible)

    def test_risk_off_raises_practical_entry_score_gate_without_changing_score(self):
        penalties = {"chase_extension": 15, "event_risk": 8}
        neutral = self.scorer.score_feature_snapshot(
            self.build_snapshot(regime="NEUTRAL", penalty_overrides=penalties)
        )
        risk_off = self.scorer.score_feature_snapshot(
            self.build_snapshot(regime="RISK_OFF", penalty_overrides=penalties)
        )
        self.assertEqual(neutral.final_score, 77.0)
        self.assertEqual(risk_off.final_score, 77.0)
        self.assertEqual(neutral.practical_entry_threshold, 75.0)
        self.assertEqual(risk_off.practical_entry_threshold, 80.0)
        self.assertTrue(neutral.score_threshold_passed)
        self.assertTrue(neutral.research_eligible)
        self.assertFalse(risk_off.score_threshold_passed)
        self.assertFalse(risk_off.research_eligible)

    def test_low_confidence_blocks_research_eligibility_even_at_high_score(self):
        result = self.scorer.score_feature_snapshot(
            self.build_snapshot(data_confidence="LOW")
        )
        self.assertEqual(result.final_score, 100.0)
        self.assertTrue(result.score_threshold_passed)
        self.assertFalse(result.research_eligible)

    def test_missing_hard_veto_check_fails_closed(self):
        snapshot = self.build_snapshot(include_hard_veto_checked=False)
        with self.assertRaises(ChampionInputError):
            self.scorer.score_feature_snapshot(snapshot)

    def test_missing_one_frozen_veto_flag_fails_closed(self):
        snapshot = self.build_snapshot(
            omit_veto_flags=(self.config.hard_veto_flags[0],)
        )
        with self.assertRaises(ChampionInputError):
            self.scorer.score_feature_snapshot(snapshot)

    def test_unavailable_required_score_feature_fails_closed(self):
        snapshot = self.build_snapshot()
        features = list(snapshot.features)
        target = "champion.technical.trend_quality"
        features = [
            FeatureValue(name=target, status="UNRESOLVED")
            if feature.name == target
            else feature
            for feature in features
        ]
        unresolved_snapshot = FeatureSnapshot.build(
            strategy_id=snapshot.strategy_id,
            sleeve=snapshot.sleeve,
            as_of=snapshot.as_of,
            data_snapshot_id=snapshot.data_snapshot_id,
            feature_set_version=snapshot.feature_set_version,
            implementation_version=snapshot.implementation_version,
            config_version=snapshot.config_version,
            features=features,
        )
        with self.assertRaises(ChampionInputError):
            self.scorer.score_feature_snapshot(unresolved_snapshot)

    def test_penalty_above_frozen_cap_is_rejected(self):
        snapshot = self.build_snapshot(
            penalty_overrides={"chase_extension": 16}
        )
        with self.assertRaises(ChampionInputError):
            self.scorer.score_feature_snapshot(snapshot)

    def test_long_sleeve_cannot_be_scored_by_short_mid_champion(self):
        snapshot = self.build_snapshot(
            strategy_id=LONG_STRATEGY_ID,
            sleeve=LONG_SLEEVE,
        )
        with self.assertRaises(ValueError):
            self.scorer.score_feature_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main()
