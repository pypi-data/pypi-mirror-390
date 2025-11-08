from unittest import TestCase

from drow.query import (
    build_arg_for_query,
    build_arg_for_query_range,
)


class TestQuery(TestCase):
    def test_query(self) -> None:
        arg = build_arg_for_query(
            "https://example.org/prometheus/",
            metric="prometheus_target_interval_length_seconds",
        )
        self.assertEqual(
            arg.url,
            "https://example.org/prometheus/api/v1/query",
        )
        self.assertEqual(
            arg.params["query"],
            "prometheus_target_interval_length_seconds",
        )

    def test_query_with_time(self) -> None:
        arg = build_arg_for_query(
            "https://example.org/prometheus/",
            metric="prometheus_target_interval_length_seconds",
            time=1435781451,
        )
        self.assertEqual(arg.params["time"], "1435781451")

    def test_query_range(self) -> None:
        start = 1435781451
        end = start + 5 * 60

        arg = build_arg_for_query_range(
            "https://example.org/prometheus/",
            metric="prometheus_target_interval_length_seconds",
            start=start,
            end=end,
        )
        self.assertEqual(
            arg.url,
            "https://example.org/prometheus/api/v1/query_range",
        )
        self.assertEqual(
            arg.params["query"],
            "prometheus_target_interval_length_seconds",
        )
        self.assertEqual(arg.params["start"], "1435781451")
        self.assertEqual(arg.params["end"], "1435781751")
        self.assertEqual(arg.params["step"], "5")

    def test_query_range_with_step(self) -> None:
        start = 1435781451
        end = start + 5 * 60

        arg = build_arg_for_query_range(
            "https://example.org/prometheus/",
            metric="prometheus_target_interval_length_seconds",
            start=start,
            end=end,
            step=15,
        )
        self.assertEqual(arg.params["step"], "15")
