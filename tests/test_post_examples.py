"""Regression checks for the corrected article examples. No cloud access."""

import ast
import contextlib
from datetime import date, timedelta
import importlib.util
import io
import json
from pathlib import Path
import random
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def load_example(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


forecast = load_example("forecast_example", "content/post/jupyter-forecast/forecast.py")
sorting = load_example("sorting_example", "content/post/python-sort/sorting.py")


def observations(values, capacity=1000):
    return [(date(2026, 1, 1) + timedelta(days=i), value, capacity)
            for i, value in enumerate(values)]


class SortingTests(unittest.TestCase):
    def test_results_match_python_sort(self):
        rng = random.Random(42)
        cases = [[], [1], [4, 3, 2, 1], [3, 1, 2], [2, 2, -1, 0], list(range(30))]
        cases += [rng.choices(range(-10, 11), k=30) for _ in range(20)]
        for algorithm in (sorting.merge_sort, sorting.selection_sort, sorting.bubble_sort):
            for original in cases:
                with self.subTest(algorithm=algorithm.__name__, original=original):
                    values = original.copy()
                    _, elapsed = algorithm(values)
                    self.assertEqual(values, sorted(original))
                    self.assertGreaterEqual(elapsed, 0)

    def test_benchmark_checks_and_reports(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            sorting.benchmark(size=50, repeats=2)
        self.assertIn("median ms", output.getvalue())


class FibonacciTests(unittest.TestCase):
    def test_all_article_variants(self):
        article = (ROOT / "content/post/dp/index.md").read_text(encoding="utf-8")
        blocks = re.findall(r"^```python\s*\n(.*?)^```", article, re.M | re.S)
        self.assertEqual(len(blocks), 5)
        for block in blocks:
            tree = ast.parse(block)
            # Exclude sample prints and benchmark runs, retain definitions/state.
            tree.body = [node for node in tree.body if isinstance(
                node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.Assign))]
            namespace = {}
            exec(compile(tree, "fibonacci_article", "exec"), namespace)
            function = next(namespace[node.name] for node in tree.body if isinstance(node, ast.FunctionDef))
            for number, expected in ((0, 0), (1, 1), (2, 1), (6, 8), (10, 55)):
                with self.subTest(function=function.__name__, number=number):
                    self.assertEqual(function(number), expected)
            for invalid in (-1, 1.5, True, "6"):
                with self.assertRaises(ValueError):
                    function(invalid)


class ForecastTests(unittest.TestCase):
    def test_constant_growth_and_first_future_day(self):
        result = forecast.project(observations([100, 110, 120, 130, 140]), horizon=61)
        self.assertEqual(result["daily_growth_bytes"], 10)
        self.assertEqual(result["forecast"][0], {"date": "2026-01-06", "used_bytes": 150})
        self.assertEqual(result["forecast"][-1]["used_bytes"], 750)
        self.assertEqual(result["days_to_limit"], 61)
        self.assertEqual(result["status"], "within_horizon")

    def test_threshold_beyond_horizon(self):
        result = forecast.project(observations([100, 110, 120, 130, 140]), horizon=60)
        self.assertEqual(result["status"], "beyond_horizon")
        self.assertIsNone(result["limit_date"])

    def test_zero_and_negative_growth(self):
        for values in ([100, 100, 100], [100, 90, 80]):
            result = forecast.project(observations(values))
            self.assertEqual(result["status"], "not_reached_nonpositive_growth")
            self.assertIsNone(result["days_to_limit"])
            self.assertGreaterEqual(min(p["used_bytes"] for p in result["forecast"]), 0)

    def test_already_reached_even_with_negative_growth(self):
        result = forecast.project(observations([850, 800, 750]))
        self.assertEqual(result["status"], "already_reached")
        self.assertEqual(result["days_to_limit"], 0)

    def test_isolated_spike_does_not_erase_typical_growth(self):
        result = forecast.project(observations([100, 110, 120, 500, 140, 150, 160]))
        self.assertEqual(result["daily_growth_bytes"], 10)
        self.assertEqual(result["used_bytes"], 160)

    def test_gaps_duplicate_days_and_capacity_change_fail(self):
        cases = [[], observations([100]), observations([100, float("nan")]),
                 observations([100, float("inf")]), observations([100, -1]),
                 observations([100, 110], capacity=0), observations([100, 1100])]
        gap = observations([100, 110, 120])
        cases.append([gap[0], gap[2]])
        cases.append([gap[0], gap[0]])
        cases.append([gap[0], (gap[1][0], 110, 2000)])
        for samples in cases:
            with self.subTest(samples=samples), self.assertRaises(ValueError):
                forecast.project(samples)

    def test_invalid_parameters(self):
        for horizon in (0, -1, 1.5, True, 3651):
            with self.assertRaises(ValueError):
                forecast.project(observations([100, 110]), horizon=horizon)
        for threshold in (0, 1.1, float("nan")):
            with self.assertRaises(ValueError):
                forecast.project(observations([100, 110]), threshold=threshold)

    def test_chronological_synthetic_holdout(self):
        samples = observations([100 + 10 * i for i in range(15)])
        result = forecast.project(samples[:10], horizon=5)
        actual = [row[1] for row in samples[10:]]
        projected = [point["used_bytes"] for point in result["forecast"]]
        self.assertEqual(projected, actual)
        self.assertGreater(sum(abs(samples[9][1] - value) for value in actual), 0)

    def test_matrix_contract(self):
        payload = {"status": "success", "data": {"resultType": "matrix", "result": [
            {"metric": {"site": "lab", "device_class": "ssd"}, "values": [[0, "100"]]}]}}
        self.assertEqual(forecast.read_matrix(payload)[("lab", "ssd")][date(1970, 1, 1)], 100)
        payload["warnings"] = ["partial data"]
        with self.assertRaises(ValueError):
            forecast.read_matrix(payload)

    def test_http_is_rejected_before_network_access(self):
        with self.assertRaises(ValueError):
            forecast.request_bytes("http://example.com")

    def test_offline_cli_writes_consistent_artifacts(self):
        with tempfile.TemporaryDirectory() as output:
            subprocess.run([sys.executable, str(ROOT / "content/post/jupyter-forecast/forecast.py"),
                            "--csv", str(ROOT / "content/post/jupyter-forecast/sample.csv"),
                            "--horizon", "90", "--output", output], check=True, capture_output=True)
            reports = json.loads((Path(output) / "forecast.json").read_text())
            self.assertEqual(len(reports), 1)
            self.assertEqual(reports[0]["daily_growth_bytes"], 10 * forecast.TIB)
            self.assertEqual(reports[0]["days_to_limit"], 60)
            self.assertEqual(len((Path(output) / "forecast.csv").read_text().splitlines()), 91)
            payload = json.loads((Path(output) / "teams-payload.json").read_text())
            self.assertEqual(payload["attachments"][0]["content"]["type"], "AdaptiveCard")


if __name__ == "__main__":
    unittest.main()
