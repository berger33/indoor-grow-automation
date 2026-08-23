from unittest import TestCase

from hub.growhub.domain.filters import MedianFilter, MovingAverageFilter


class MedianFilterTests(TestCase):
    def test_rejects_outlier_in_sliding_window(self) -> None:
        sample_filter = MedianFilter(3)
        self.assertEqual(6.0, sample_filter.add(6.0))
        self.assertEqual(6.1, sample_filter.add(6.2))
        self.assertEqual(6.2, sample_filter.add(99.0))
        self.assertEqual(6.3, sample_filter.add(6.3))

    def test_reports_actual_warmup_count(self) -> None:
        sample_filter = MedianFilter(5)
        sample_filter.add(1.0)
        self.assertEqual(1, sample_filter.sample_count)

    def test_rejects_invalid_window_and_non_finite_sample(self) -> None:
        with self.assertRaises(ValueError):
            MedianFilter(0)
        with self.assertRaises(ValueError):
            MedianFilter(3).add(float("inf"))


class MovingAverageFilterTests(TestCase):
    def test_uses_only_samples_present_during_warmup(self) -> None:
        sample_filter = MovingAverageFilter(3)
        self.assertEqual(10.0, sample_filter.add(10.0))
        self.assertEqual(15.0, sample_filter.add(20.0))

    def test_discards_oldest_sample_after_window_fills(self) -> None:
        sample_filter = MovingAverageFilter(3)
        for value in (1.0, 2.0, 3.0):
            sample_filter.add(value)
        self.assertEqual(3.0, sample_filter.add(4.0))
        self.assertEqual(3, sample_filter.sample_count)

    def test_rejects_boolean_window_and_nan(self) -> None:
        with self.assertRaises(ValueError):
            MovingAverageFilter(True)
        with self.assertRaises(ValueError):
            MovingAverageFilter(2).add(float("nan"))
