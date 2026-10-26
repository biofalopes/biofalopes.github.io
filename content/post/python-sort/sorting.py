"""Correctness first: time the outer call, not recursive subproblems."""

from functools import wraps
from random import Random
from statistics import median
from time import perf_counter
import platform


def timed(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = function(*args, **kwargs)
        return result, perf_counter() - start
    return wrapper


@timed
def merge_sort(values):
    def sort(items):
        if len(items) < 2:
            return
        middle = len(items) // 2
        left, right = items[:middle], items[middle:]
        sort(left)
        sort(right)
        i = j = k = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                items[k] = left[i]
                i += 1
            else:
                items[k] = right[j]
                j += 1
            k += 1
        items[k:] = left[i:] + right[j:]
    sort(values)


@timed
def selection_sort(values):
    for i in range(len(values)):
        minimum = i
        for j in range(i + 1, len(values)):
            if values[j] < values[minimum]:
                minimum = j
        values[i], values[minimum] = values[minimum], values[i]


@timed
def bubble_sort(values):
    for end in range(len(values) - 1, 0, -1):
        swapped = False
        for i in range(end):
            if values[i] > values[i + 1]:
                values[i], values[i + 1] = values[i + 1], values[i]
                swapped = True
        if not swapped:
            break


def benchmark(size=1000, repeats=5, seed=42):
    original = Random(seed).sample(range(size * 10), size)
    expected = sorted(original)
    print(f"Python {platform.python_version()} | {platform.system()} {platform.machine()}")
    print(f"{size} distinct integers | seed={seed} | {repeats} repetitions | median ms")
    for algorithm in (merge_sort, selection_sort, bubble_sort):
        samples = []
        for _ in range(repeats):
            values = original.copy()  # Copying is outside the timed section.
            _, elapsed = algorithm(values)
            if values != expected:
                raise AssertionError(f"{algorithm.__name__} did not sort correctly")
            samples.append(elapsed * 1000)
        print(f"{algorithm.__name__}: {median(samples):.3f}")


if __name__ == "__main__":
    benchmark()
