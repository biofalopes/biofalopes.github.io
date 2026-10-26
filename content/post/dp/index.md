+++
slug = "dynamic-programmingdp"
lastmod = "2026-10-26"
title = "Dynamic Programming(DP)"
description = "Studying DP in Python with Fibonacci"
date = "2025-03-07"
draft = false
toc = true
tags = ["python"]
categories = ["python"]
image = "fib.png"
author = "Fabio M. Lopes"
+++

Dynamic Programming (DP). Simply put, it's a powerful algorithmic technique used mainly to solve optimization problems, especiallly those that exhibit two key properties: ***optimal substructure*** and ***overlapping subproblems***. Understanding these two properties is crucial to grasping the essence of DP.

*   ***Optimal Substructure***: A problem exhibits optimal substructure if an optimal solution to the overall problem can be constructed from optimal solutions to its subproblems. In plain English, if the best way to solve the *big* problem involves using the best solutions to smaller, related problems, then you have optimal substructure. A classic example? Shortest path algorithms. The shortest path from point A to point B necessarily includes the shortest paths to the intermediate points along the way.

*   ***Overlapping Subproblems***: This means that the problem can be broken down into subproblems which are reused multiple times. A naive recursive approach would repeatedly solve the same subproblems, leading to exponential time complexity. DP avoids this by solving each subproblem only once and storing the result, saving time and improving efficiency.

Let's consider a well-known example: the Fibonacci sequence. The nth Fibonacci number is defined as the sum of the (n-1)th and (n-2)th Fibonacci numbers.

**Naive Recursive Approach (Inefficient):**

```python
def fibonacci(n):
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError("n must be a non-negative integer")
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

As *n* grows, the number of redundant calculations explodes.

The examples accept non-negative integers, including `0` and `1`. Invalid inputs raise `ValueError`.

Now, let's look at how Dynamic Programming can solve the same problem using two common approaches:

**1. Top-Down with Memoization:**

Memoization is essentially caching the results of expensive function calls and reusing them when the same inputs occur again. We start from the top (the original problem) and recursively break it down, storing the results in a dictionary (or similar data structure) to avoid redundant calculations.

```python
def fibonacci_memoization(n, memo=None):
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError("n must be a non-negative integer")
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci_memoization(n-1, memo) + fibonacci_memoization(n-2, memo)
    return memo[n]

print(fibonacci_memoization(6))
```

**2. Bottom-Up (Tabulation):**

Tabulation involves building a table (usually an array or matrix) from the bottom up, starting with the base cases and iteratively computing the solutions to larger subproblems based on the solutions to smaller ones.

```python
def fibonacci_tabulation(n):
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError("n must be a non-negative integer")
    if n <= 1:
        return n
    table = [0] * (n + 1)
    table[1] = 1
    for i in range(2, n + 1):
        table[i] = table[i-1] + table[i-2]
    return table[n]

print(fibonacci_tabulation(0))  # 0
print(fibonacci_tabulation(1))  # 1
print(fibonacci_tabulation(6))  # 8
```

**Key differences between Memoization and Tabulation:**
*   **Memoization (Top-Down):** Recursive approach, starts from the original problem, and caches results as needed. Can be more intuitive for some problems.
*   **Tabulation (Bottom-Up):** Iterative approach, builds the solution from the base cases up. Can be more efficient in terms of space complexity in some cases, as it may not need to store the entire call stack.

**When to Use Dynamic Programming?**
*   The problem can be divided into overlapping subproblems.
*   The problem exhibits optimal substructure.
*   You want to optimize the performance of a recursive solution that is repeatedly solving the same subproblems.

**Common Applications of Dynamic Programming:**
*   ***Knapsack Problem***: Optimizing the selection of items to maximize value while respecting a weight constraint.
*   ***Longest Common Subsequence (LCS)***: Finding the longest sequence of characters common to two strings.
*   ***Edit Distance***: Calculating the minimum number of operations (insertions, deletions, substitutions) required to transform one string into another.
*   ***Shortest Path Algorithms*** (e.g., Floyd-Warshall): Finding the shortest paths between all pairs of vertices in a graph.

I wrote two python programs, one using top-down and another using bottom-up. They calculate fib(500) and print the number of iterations, cache hits, function calls and the elapsed time. It is a good way to compare how the different approaches can influence the performance. When i tried to run the top-down program for fib(1000), i reached the recursion limit. Using `functools.lru_cache` can replace the dictionary, but it does not remove recursive call depth. The iterative version avoids that recursion limit. The global counters in the instrumentation examples below describe a fresh process run; reset them and the cache before comparing repeated runs.

<details>
<summary><b>Fibonacci Top-Down Example</b> (Click to Show/Hide)</summary>

```python
import time

cache = {0:0, 1:1}
calls = 0
cache_hits = 0

def fib(n: int) -> int:
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError("n must be a non-negative integer")
    global calls, cache_hits
    if n in cache:
        cache_hits += 1
        return cache[n]
    else:
        calls += 1
        cache[n] = fib(n-1) + fib(n-2)
        return cache[n]

if __name__ == '__main__':
    n = 500

    start_time = time.perf_counter()
    result = fib(n)
    end_time = time.perf_counter()

    elapsed_time_ms = (end_time - start_time) * 1000

    print(f'{result}')
    print(f'{calls} function calls and {cache_hits} cache hits.')
    print(f"Elapsed time: {elapsed_time_ms:.4f} ms")
```
</details>

<details>
<summary><b>Fibonacci Bottom-Up Example</b> (Click to Show/Hide)</summary>

```python
import time

iterations = 0

def fib(n: int) -> int:
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError("n must be a non-negative integer")
    global iterations

    if n == 0:
        return 0
    elif n == 1:
        return 1

    fibonacci = [0] * (n + 1)
    fibonacci[0] = 0
    fibonacci[1] = 1

    for i in range(2, n + 1):
        iterations += 1
        fibonacci[i] = fibonacci[i - 1] + fibonacci[i - 2]

    return fibonacci[n]

if __name__ == '__main__':
    n = 500
    start_time = time.perf_counter()
    result = fib(n)
    end_time = time.perf_counter()
    elapsed_time_ms = (end_time - start_time) * 1000

    print(f'{result}')
    print(f'{iterations} iterations.')
    print(f"Elapsed time: {elapsed_time_ms:.4f} ms")
```
</details>

## Revision note

October 2026: fixed the tabulation base case for zero, removed the shared mutable default argument from memoization, and added input validation. Memoization still consumes call-stack space; it does not make recursion depth unlimited.
