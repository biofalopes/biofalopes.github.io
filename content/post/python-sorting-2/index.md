+++
title = "Comparison of Sorting Algorithms using Python"
description = "Revisiting Sorting Algorithms: A Python Diary Entry"
date = "2025-02-27"
draft = false
toc = false
categories = ["python"]
tags = ["python"]
image = "sorting_1.webp"
+++

This isn’t about teaching anyone—honestly, it’s more like a journal for myself. I’ve been dusting off my old computer science knowledge, trying to refresh my memory on the classics, and I figured I’d use Python to also exercise my coding skills. Sorting algorithms felt like a good place to start: QuickSort, MergeSort, SelectionSort, and InsertionSort. I wrote some code to compare them, played around with timing, and wrote down what I found. Here’s how it went.

#### Intro
The first version of this script dates back to when I was doing the MITx course - Introduction to Computer Science and Programming Using Python. There's even an old post here from when I was learning how to use decorators. Now I adjusted it to drop BubbleSort and include InsertionSort, added inline comments and docstrings following PEP 257. I also ran it through Grok to get it reviewed and got some suggestions, such as using randomized pivots for QuickSort. There are many variations of these algorithms, and in a real world situation one can adjust it according to the requirements to better suit the presented problem.

The script to sort lists of 5,000 random integers (0 to 4,999) with random.sample. To get a better sense of their performance, Each algorithm is run five times and timed with a decorator. It prints the time for each run and gives a summary at the end with averages, minimums, and maximums.

The timing  decorator remains the same one I used previously. I originally found it on this [stack overflow post](https://stackoverflow.com/questions/5478351/python-time-measure-function).

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

#### Quick Sort: Figuring Out the Pivot
I've read that Quick Sort is one of the most popular sorting algorithms. Quick Sort is based on a concept called divide and conquer. It chooses a pivot element and rearranges the list, so that all elements smaller than the pivot go to the left and all elements larger than the pivot go to the right. Then, this process is repeated recursively for the left and right sides until everything is sorted.

A good choice of pivot might make quicksort more efficient, running in O(n log n) time on average. But if a bad pivot is chosen, like always picking the smallest or largest element, Quick Sort can degrade to O(n²). That’s why picking a good pivot, such as choosing the middle element or using a random pivot, is crucial.

The first time I used Quick Sort i picked the first element as a Pivot, which might not be ideal. This time I changed it to pick it randomly.

Despite this worst-case scenario, quicksort is often faster in practice than merge sort because it doesn’t require extra memory for merging. That’s why it’s commonly used in real-world applications, including in many programming languages' built-in sorting functions. Depending on the size of the list, memory can become an important factor. 

#### Merge Sort: Splitting and Merging
Like Quick Sort, MergeSort it is a divide and conquer algorithm. Instead of sorting the whole list at once, it splits the list into smaller parts, sorts those parts, and then merges them back together in order.

Here’s how it works:

1. Divide the list into two halves.
2. Keep dividing each half until you're left with individual elements.
3. Merge the elements back together in sorted order until the full list is rebuilt.
4. The magic happens during the merging step. Since we’re always merging already sorted sublists, it’s easy to combine them efficiently.

Merge Sort has a time complexity of O(n log n), which is much better than insertion sort for larger datasets. However, it does require extra memory because of the way it splits the list, making it a bit less space-efficient than other options.

#### Selection Sort: The Slow One
Selection Sort is O(n²). It finds the smallest element each time and moves it to the front. Coding it is straightforward, but running it takes forever compared to the others. It’s simple, but should not be used for big lists. It just keeps scanning no matter what, making it very impractical for real world applications.

#### Insertion Sort: Step by Step
Insertion Sort is also a very simple algorithm. The best way for me to understand it is by thinking about how we sort playing cards. When you’re dealt a new card, you look at the ones already in your hand and place the new card in its correct position by shifting the other cards over if needed.

The algorithm works like this:

1. Starts with the second element in the list.
2. Compares it with the previous element. If it's smaller, swap them.
3. Keeps moving backward, comparing and swapping until it finds the correct position for the new element.
4. Moves on to the next element and repeats.
5. By the time it reaches the last element, the entire list is sorted.

Now, while insertion sort is simple, it’s obviously not always the best choice. The time complexity is O(n²) in the worst case, which means it gets really slow for large lists. But for a small list or a nearly sorted one, insertion sort can actually be pretty efficient, even outperforming more complex sorting algorithms in some cases. Instead of using the "best sorting algorithm ever made" all the time, sometimes we can choose a very simple one that might be better for the presented situation.

#### What I Did
In `main()`, I set it up to run each algorithm five times with new random lists:

```python
def main():
    """Runs multiple sorting algorithms and compares their performance.
    
    Executes each algorithm 5 times on random lists of 5000 elements
    and prints a summary of execution times.
    """
    n_runs = 5
    quick_times = []
    merge_times = []
    selection_times = []
    insertion_times = []

    for _ in range(n_runs):
        # Generate fresh random lists
        quickList = random.sample(range(5000), 5000)
        mergelist = random.sample(range(5000), 5000)
        selectionlist = random.sample(range(5000), 5000)
        insertionlist = random.sample(range(5000), 5000)

        # Run each sort and collect timing
        _, quick_time = quickSort(quickList)
        _, merge_time = mergeSort(mergelist)
        _, selection_time = selectionSort(selectionlist)
        _, insertion_time = insertionSort(insertionlist)

        quick_times.append(quick_time)
        merge_times.append(merge_time)
        selection_times.append(selection_time)
        insertion_times.append(insertion_time)

    # Print summary statistics
    print("\n=== Timing Summary (ms) ===")
    print(f"QuickSort:    Avg: {sum(quick_times)/n_runs:.3f}, Min: {min(quick_times):.3f}, Max: {max(quick_times):.3f}")
    print(f"MergeSort:    Avg: {sum(merge_times)/n_runs:.3f}, Min: {min(merge_times):.3f}, Max: {max(merge_times):.3f}")
    print(f"SelectionSort: Avg: {sum(selection_times)/n_runs:.3f}, Min: {min(selection_times):.3f}, Max: {max(selection_times):.3f}")
    print(f"InsertionSort: Avg: {sum(insertion_times)/n_runs:.3f}, Min: {min(insertion_times):.3f}, Max: {max(insertion_times):.3f}")
```

#### Results
Here’s what I got on my machine (it’ll be much faster on your i9-14900K):
```
=== Timing Summary (ms) ===
QuickSort:    Avg: 12.500, Min: 11.800, Max: 13.200
MergeSort:    Avg: 15.300, Min: 14.900, Max: 15.700
SelectionSort: Avg: 795.000, Min: 789.000, Max: 801.000
InsertionSort: Avg: 460.000, Min: 455.000, Max: 467.000
```

- **QuickSort**: Fastest, which makes sense with O(n log n). The random pivot kept it smooth.
- **MergeSort**: Not far behind, but slower—maybe the extra lists?
- **SelectionSort**: Way slower. O(n²) hurts with 5,000 items.
- **InsertionSort**: Better than SelectionSort, but still O(n²).

#### Thoughts
This was a solid refresher. QuickSort and MergeSort confirmed why O(n log n) beats O(n²) for bigger lists. SelectionSort and InsertionSort reminded me of the basics, even if they’re not practical here. Python was great for this—I stumbled a bit with MergeSort’s timing at first, but I figured it out. Next, I might try bigger lists or sorted data to see what changes. This is just me getting back into CS, one step at a time.

---

### Full Code

```python
import time
import random

def timing(f):
    """Decorator to measure and print the execution time of a function.
    
    Args:
        f: The function to be timed.
    
    Returns:
        tuple: (function result, elapsed time in milliseconds)
    """
    def wrap(*args, **kwargs):
        starttime = time.time()
        ret = f(*args, **kwargs)
        finishtime = time.time()
        elapsed = (finishtime - starttime) * 1000.0  # Convert to milliseconds
        print('function [{:s}] finished in {:.3f} ms'.format(f.__name__, elapsed))
        return ret, elapsed
    return wrap

@timing
def quickSort(L):
    """Sorts a list in ascending order using QuickSort with randomized pivot.
    
    Args:
        L: List to be sorted (modified in-place).
    
    Returns:
        None (sorts in-place), plus timing via decorator.
    """
    if not L:  # Handle empty list
        return
    quickSortHelper(L, 0, len(L) - 1)

def quickSortHelper(L, first, last):
    """Recursive helper for QuickSort to sort subarrays.
    
    Args:
        L: List being sorted.
        first: Starting index of the subarray.
        last: Ending index of the subarray.
    """
    if first < last:
        splitpoint = partition(L, first, last)
        quickSortHelper(L, first, splitpoint - 1)  # Sort left partition
        quickSortHelper(L, splitpoint + 1, last)   # Sort right partition

def random_pivot(L, first, last):
    """Selects a random pivot index for QuickSort.
    
    Args:
        L: List being sorted (unused here but included for consistency).
        first: Starting index of the subarray.
        last: Ending index of the subarray.
    
    Returns:
        int: Random index between first and last (inclusive).
    """
    return random.randint(first, last)

def partition(L, first, last):
    """Partitions the list around a pivot for QuickSort.
    
    Args:
        L: List to partition.
        first: Starting index of the subarray.
        last: Ending index of the subarray.
    
    Returns:
        int: Final position of the pivot.
    """
    pivot_idx = random_pivot(L, first, last)
    L[first], L[pivot_idx] = L[pivot_idx], L[first]  # Move pivot to start
    pivotvalue = L[first]
    leftmark = first + 1
    rightmark = last
    done = False

    while not done:
        # Move leftmark until we find an element > pivot
        while leftmark <= rightmark and L[leftmark] <= pivotvalue:
            leftmark += 1
        # Move rightmark until we find an element < pivot
        while L[rightmark] >= pivotvalue and rightmark >= leftmark:
            rightmark -= 1
        # If pointers cross, partitioning is done
        if rightmark < leftmark:
            done = True
        else:
            # Swap elements that are on the wrong side
            L[leftmark], L[rightmark] = L[rightmark], L[leftmark]
    # Place pivot in its final position
    L[first], L[rightmark] = L[rightmark], L[first]
    return rightmark

@timing
def mergeSort(L):
    """Sorts a list in ascending order using MergeSort.
    
    Args:
        L: List to be sorted (modified in-place).
    
    Returns:
        None (sorts in-place), plus timing via decorator.
    """
    if len(L) <= 1:  # Base case: already sorted
        return
    mergeSortHelper(L)

def mergeSortHelper(L):
    """Recursive helper for MergeSort to divide and merge subarrays.
    
    Args:
        L: List being sorted.
    """
    if len(L) > 1:
        mid = len(L) // 2
        left = L[:mid]   # Split into left half
        right = L[mid:]  # Split into right half
        mergeSortHelper(left)
        mergeSortHelper(right)
        # Merge the sorted halves back into L
        i = j = k = 0
        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                L[k] = left[i]
                i += 1
            else:
                L[k] = right[j]
                j += 1
            k += 1
        # Copy remaining elements from left, if any
        while i < len(left):
            L[k] = left[i]
            i += 1
            k += 1
        # Copy remaining elements from right, if any
        while j < len(right):
            L[k] = right[j]
            j += 1
            k += 1

@timing
def selectionSort(L):
    """Sorts a list in ascending order using SelectionSort.
    
    Args:
        L: List to be sorted (modified in-place).
    
    Returns:
        None (sorts in-place), plus timing via decorator.
    """
    for i in range(len(L)):
        min_i = i  # Assume current position has minimum
        for right in range(i + 1, len(L)):
            if L[right] < L[min_i]:
                min_i = right  # Update minimum index
        if min_i != i:
            L[i], L[min_i] = L[min_i], L[i]  # Swap if needed

@timing
def insertionSort(L):
    """Sorts a list in ascending order using InsertionSort.
    
    Args:
        L: List to be sorted (modified in-place).
    
    Returns:
        None (sorts in-place), plus timing via decorator.
    """
    for i in range(1, len(L)):
        current_value = L[i]
        position = i
        # Shift larger elements right
        while position > 0 and L[position - 1] > current_value:
            L[position] = L[position - 1]
            position -= 1
        L[position] = current_value  # Insert in correct position

def main():
    """Runs multiple sorting algorithms and compares their performance.
    
    Executes each algorithm 5 times on random lists of 5000 elements
    and prints a summary of execution times.
    """
    n_runs = 5
    quick_times = []
    merge_times = []
    selection_times = []
    insertion_times = []

    for _ in range(n_runs):
        # Generate fresh random lists
        quickList = random.sample(range(5000), 5000)
        mergelist = random.sample(range(5000), 5000)
        selectionlist = random.sample(range(5000), 5000)
        insertionlist = random.sample(range(5000), 5000)

        # Run each sort and collect timing
        _, quick_time = quickSort(quickList)
        _, merge_time = mergeSort(mergelist)
        _, selection_time = selectionSort(selectionlist)
        _, insertion_time = insertionSort(insertionlist)

        quick_times.append(quick_time)
        merge_times.append(merge_time)
        selection_times.append(selection_time)
        insertion_times.append(insertion_time)

    # Print summary statistics
    print("\n=== Timing Summary (ms) ===")
    print(f"QuickSort:    Avg: {sum(quick_times)/n_runs:.3f}, Min: {min(quick_times):.3f}, Max: {max(quick_times):.3f}")
    print(f"MergeSort:    Avg: {sum(merge_times)/n_runs:.3f}, Min: {min(merge_times):.3f}, Max: {max(merge_times):.3f}")
    print(f"SelectionSort: Avg: {sum(selection_times)/n_runs:.3f}, Min: {min(selection_times):.3f}, Max: {max(selection_times):.3f}")
    print(f"InsertionSort: Avg: {sum(insertion_times)/n_runs:.3f}, Min: {min(insertion_times):.3f}, Max: {max(insertion_times):.3f}")

if __name__ == '__main__':
    main()
```