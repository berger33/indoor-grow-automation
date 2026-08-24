from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.control.nutrient_batch import (
    BatchAction,
    BatchState,
    NutrientBatchController,
    NutrientChannel,
    NutrientRecipe,
)


class NutrientBatchControllerTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, tzinfo=UTC)
        self.recipe = NutrientRecipe(20, 1.5, 1, 2, 3, 4)
        self.controller = NutrientBatchController()
        self.controller.start(
            self.recipe,
            now=self.now,
            tank_capacity_l=50,
            stock_ml={channel: 1_000 for channel in NutrientChannel},
        )

    def advance(self, seconds, volume=20, safe=True):
        return self.controller.advance(
            now=self.now + timedelta(seconds=seconds),
            current_volume_l=volume,
            safe_to_operate=safe,
        )

    def test_fills_then_doses_recipe_in_fixed_order(self) -> None:
        self.assertEqual(BatchAction.FILL_WATER, self.advance(0, volume=19).action)
        self.assertEqual(
            BatchAction.START_MIXING_AND_STIRRERS, self.advance(1).action
        )
        first = self.advance(6)
        self.assertEqual(NutrientChannel.CALMAG, first.channel)
        self.assertEqual(20, first.volume_ml)

        expected = (
            (66, NutrientChannel.MICRO, 40),
            (126, NutrientChannel.BLOOM, 60),
            (186, NutrientChannel.GROW, 80),
        )
        for seconds, channel, volume in expected:
            decision = self.advance(seconds)
            self.assertEqual(channel, decision.channel)
            self.assertEqual(volume, decision.volume_ml)
        complete = self.advance(246)
        self.assertEqual(BatchAction.STOP_STIRRERS, complete.action)
        self.assertEqual(BatchState.READY_FOR_DILUTION, complete.state)

    def test_validates_capacity_and_stock_before_start(self) -> None:
        other = NutrientBatchController()
        with self.assertRaisesRegex(ValueError, "capacidade"):
            other.start(
                self.recipe,
                now=self.now,
                tank_capacity_l=10,
                stock_ml={channel: 1_000 for channel in NutrientChannel},
            )
        with self.assertRaisesRegex(ValueError, "estoque insuficiente"):
            other.start(
                self.recipe,
                now=self.now,
                tank_capacity_l=50,
                stock_ml={channel: 0 for channel in NutrientChannel},
            )

    def test_aborts_all_outputs_on_safety_interlock(self) -> None:
        decision = self.advance(0, volume=10, safe=False)
        self.assertEqual(BatchAction.ABORT_ALL, decision.action)
        self.assertEqual(BatchState.ABORTED, decision.state)
        self.assertEqual(BatchAction.HOLD, self.advance(1).action)

    def test_prevents_overlapping_batches(self) -> None:
        with self.assertRaisesRegex(PermissionError, "execução"):
            self.controller.start(
                self.recipe,
                now=self.now,
                tank_capacity_l=50,
                stock_ml={channel: 1_000 for channel in NutrientChannel},
            )

    def test_rejects_invalid_recipe_ranges(self) -> None:
        with self.assertRaises(ValueError):
            NutrientRecipe(20, 1.5, 0, 0, 0, 0)
        with self.assertRaises(ValueError):
            NutrientRecipe(100, 1.5, 1, 1, 1, 1)
