"""Regression checks for the corrected article examples. No cloud access."""

import ast
import contextlib
import importlib.util
import io
from pathlib import Path
import random
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def load_example(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sorting = load_example("sorting_example", "content/post/python-sort/sorting.py")



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



if __name__ == "__main__":
    unittest.main()
