from unittest import TestCase

from hub.growhub.domain.filters import MedianFilter


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
