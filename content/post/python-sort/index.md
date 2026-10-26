+++
slug = "comparison-of-sorting-algorithms-using-python-decorators"
lastmod = "2026-10-26"
title = "Comparison of Sorting Algorithms using Python Decorators"
description = "Measuring runtime of sorting algorithms using Python decorators"
date = "2020-11-17"
draft = false
toc = true
categories = ["python"]
tags = ["python"]
image = "decorators.jpg"
+++

I wrote this exercise while learning Python decorators and sorting algorithms. The goal was to time an operation without putting timing code inside every algorithm.

**Technical revision — October 2026:** the original decorator skipped recursive calls in MergeSort, and SelectionSort swapped elements outside its outer loop. Those implementations did not reliably sort the input, so their published timings were not a valid comparison. The corrected example below checks every result against Python's `sorted` before reporting a measurement.

## Time the outer operation

A decorator wraps a function and can add behavior around its execution. Here, `timed` returns the function's result and its elapsed time in seconds, measured with `perf_counter`. This intentionally changes the return contract to a pair; a timing decorator is not automatically transparent to its caller.

MergeSort uses an undecorated recursive helper. Every recursive call executes normally, while the decorator times the complete outer operation once. SelectionSort swaps inside the outer loop, after finding the minimum of the remaining suffix. All three implementations modify the supplied list in place.

## Corrected example

Download [sorting.py](sorting.py). It uses only the Python standard library.

{{< code-file file="sorting.py" lang="python" >}}

Run it with:

```bash
python sorting.py
```

## Reading the measurements

The benchmark uses 1,000 distinct integers generated with seed 42, five repetitions per algorithm, and reports the median elapsed time. Each run starts with a fresh copy of the same list. Copying the input and verifying the result happen outside the timed section. The output records the Python version and operating-system architecture.

These timings describe this implementation and this input on the machine running it. They are not a universal ranking: already sorted inputs, duplicates, interpreter versions and machine load affect measurements. Before drawing performance conclusions, repeat the comparison across those cases and include Python's built-in sort as a practical baseline.

For these implementations, MergeSort takes O(n log n) time and O(n) auxiliary storage; SelectionSort takes O(n²) time. BubbleSort takes O(n²) in the worst case and stops early when a pass makes no swaps.

The original invalid benchmark results have been removed. The executable example generates new measurements and refuses to report a timing for an incorrect result.

## References

- [Python: perf_counter](https://docs.python.org/3/library/time.html#time.perf_counter)
- [Python: functools.wraps](https://docs.python.org/3/library/functools.html#functools.wraps)
- [Python: timeit](https://docs.python.org/3/library/timeit.html)
