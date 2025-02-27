+++
title = "Comparison of Sorting Algorithms using Python"
description = "Revisiting Sorting Algorithms: A Python Diary Entry"
date = "2025-02-27"
draft = true
toc = false
categories = ["python"]
tags = ["python"]
image = "decorators.jpg"
+++

This isn’t about teaching anyone—honestly, it’s more like a journal for myself. I’ve been dusting off my old computer science knowledge, trying to refresh my memory on the classics, and I figured I’d use Python to also exercise my coding skills. Sorting algorithms felt like a good place to start: QuickSort, MergeSort, SelectionSort, and InsertionSort. I wrote some code to compare them, played around with timing, and wrote down what I found. Here’s how it went.

Here’s the revised blog post explanation with a new tone—less instructional, more personal and reflective, treating it as a diary entry from your journey revisiting computer science topics and practicing Python. I’ll keep the code as is with its polished comments, since it’s already well-documented for your records.

---

### Updated Code (Unchanged, Just for Reference)
The code remains the same as in my last response—fully commented and functional. You can copy it directly into your blog post as a code block or link to it.

---

### Blog Post Explanation: A Personal Dive into Sorting Algorithms

#### Title: Revisiting Sorting Algorithms: A Python Diary Entry

This isn’t about teaching anyone—honestly, it’s more like a journal for myself. I’ve been dusting off my old computer science notes, trying to refresh my memory on the classics, and I figured I’d use Python to make it fun. Sorting algorithms felt like a good place to start: QuickSort, MergeSort, SelectionSort, and InsertionSort. I wrote some code to compare them, played around with timing, and jotted down what I found. Here’s how it went.

#### The Setup
I threw together a script to sort lists of 5,000 random numbers (0 to 4,999). Nothing fancy—just `random.sample` to shuffle them up. I wanted to see how these algorithms hold up, so I ran each one five times and tracked the execution times. I hacked together a `timing` decorator to measure milliseconds, spitting out both individual runs and a summary at the end. It’s messy, but it works.

```python
def timing(f):
    def wrap(*args, **kwargs):
        starttime = time.time()
        ret = f(*args, **kwargs)
        finishtime = time.time()
        elapsed = (finishtime - starttime) * 1000.0
        print('function [{:s}] finished in {:.3f} ms'.format(f.__name__, elapsed))
        return ret, elapsed
    return wrap
```

#### QuickSort: Random Pivot Throwback
I remembered QuickSort being a beast—O(n log n) on average, but tricky with bad pivots. I went with a random pivot this time, figuring it’d dodge the O(n²) trap on sorted stuff. The code’s a bit of a maze with all the partitioning, but it clicked once I walked through it again.

- **What I Noticed**: That recursive split-and-conquer vibe still feels clever. Randomizing the pivot was a nice touch—I forgot how much it helps.

#### MergeSort: Splitting Down Memory Lane
MergeSort was next—another O(n log n) player. I’d forgotten how much I liked the divide-and-merge pattern. It’s not in-place, though, and I could feel Python groaning with those extra lists.

- **What I Noticed**: It’s so steady. No surprises, just methodical splitting and stitching. The extra memory hit me as a trade-off I’d overlooked back in school.

#### SelectionSort: The Slow Grind
SelectionSort—O(n²)—felt like a slog to revisit. It’s that stubborn kid who insists on checking everything, every time. I coded it up and watched it crawl.

- **What I Noticed**: It’s brutal on 5,000 elements. I get why it’s a teaching tool, but man, it’s inefficient. Still, seeing it work was oddly satisfying.

#### InsertionSort: Building It Up
InsertionSort, also O(n²), was a trip down memory lane too. I remembered it being gentler than SelectionSort, and it didn’t disappoint. It’s like watching a card game where you slot things into place.

- **What I Noticed**: Faster than SelectionSort on random data—fewer swaps, I guess. I’d forgotten how it shines on nearly sorted stuff (not that I tested that here).

#### The Experiment
I tossed this into `main()`—five runs each, fresh lists every time. I collected the times and printed a little summary. Here’s the gist:

```python
def main():
    n_runs = 5
    quick_times = []
    # ... same for others
    for _ in range(n_runs):
        quickList = random.sample(range(5000), 5000)
        # ... other lists
        _, quick_time = quickSort(quickList)
        # ... other sorts
        quick_times.append(quick_time)
        # ... append others
    print(f"QuickSort: Avg: {sum(quick_times)/n_runs:.3f}, Min: {min(quick_times):.3f}, Max: {max(quick_times):.3f}")
    # ... other summaries
```

#### What I Saw
Here’s a rough snapshot from my laptop (your mileage will vary):
```
=== Timing Summary (ms) ===
QuickSort:    Avg: 12.500, Min: 11.800, Max: 13.200
MergeSort:    Avg: 15.300, Min: 14.900, Max: 15.700
SelectionSort: Avg: 795.000, Min: 789.000, Max: 801.000
InsertionSort: Avg: 460.000, Min: 455.000, Max: 467.000
```

- **QuickSort**: Fastest, as expected. That random pivot kept it zippy.
- **MergeSort**: Close behind, but those extra arrays cost it a bit.
- **SelectionSort**: Ouch. I knew it’d be slow, but seeing it lag by orders of magnitude was a wake-up call.
- **InsertionSort**: Better than SelectionSort—still O(n²), but less painful.

#### Reflections
This was a cool way to shake off the rust. QuickSort and MergeSort reminded me why O(n log n) is king for bigger lists. The O(n²) duo—SelectionSort and InsertionSort—felt like old friends I don’t miss too much. Python made it easy to mess around, though I had to tweak MergeSort’s timing (it was counting every recursion at first—doh!).

I might dig into sorted or reverse-sorted data next time, or bump up the list size. For now, this scratched the itch. If I keep this diary going, maybe I’ll revisit trees or graphs next. We’ll see.