+++ 
title = "Studying C Sharp from Python" 
description = "Studying C Sharp from Python with the assistance of AI" 
date = "2025-03-08" 
draft = false 
toc = false 
tags = ["python", "csharp"] 
categories = ["python", "csharp"] 
image = "banner.jpg" 
author = "Fabio M. Lopes" 
+++

In this post, I'm going to analyze the implementation of the Fibonacci sequence in Python and C#, highlighting the main differences in syntax and programming concepts. I'll also explore some essential C# principles to ease the transition for Python developers. I have a friend who is passionate about .NET. Whenever I show her a snippet of Python code, she wrinkles her nose and says, "Why use Python? .NET is so much better!" So, in her honor, I decided to convert this Python code to C# and study the process step by step. I used AI to generate the C# code and explain the differences. I found this approach fantastic for learning, and I intend to delve deeper into C# in parallel using this study method.

![dotineti](dotineti.gif)

### Python Code:
Here’s the Python implementation of the Fibonacci sequence with memoization, tracking function calls and cache hits:

```python
import time

cache = {0:0, 1:1}
calls = 0
cache_hits = 0

def fib(n: int) -> int:
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

### Translation to C#:
Below is the C# equivalent, translated using Gemini:

```csharp
using System;
using System.Collections.Generic;
using System.Diagnostics;

public class Fibonacci
{
    private static Dictionary<int, long> cache = new Dictionary<int, long> { { 0, 0 }, { 1, 1 } };
    private static long calls = 0;
    private static long cacheHits = 0;

    public static long Fib(int n)
    {
        if (cache.ContainsKey(n))
        {
            cacheHits++;
            return cache[n];
        }
        else
        {
            calls++;
            cache[n] = Fib(n - 1) + Fib(n - 2);
            return cache[n];
        }
    }

    public static void Main(string[] args)
    {
        int n = 500;

        Stopwatch stopwatch = new Stopwatch();
        stopwatch.Start();

        long result = Fib(n);

        stopwatch.Stop();
        double elapsedTimeMs = stopwatch.Elapsed.TotalMilliseconds;

        Console.WriteLine(result);
        Console.WriteLine($"{calls} function calls and {cacheHits} cache hits.");
        Console.WriteLine($"Elapsed time: {elapsedTimeMs:F4} ms");
    }
}
```

### Key Concepts for Python Developers Transitioning to C#
This section highlights the core concepts you'll encounter when moving from Python to C#, focusing on areas where the differences are most pronounced.

*   **Static Typing:** Unlike Python's dynamic typing, C# requires explicit type declarations (e.g., `int age = 30;`). This enforces type safety at compile time, catching potential errors early. You'll need to become familiar with common C# data types like `int`, `double`, `string`, `bool`, `char`, and `long` (used for larger integer values).
*   **Object-Oriented Programming (OOP) Paradigm:** C# is fundamentally object-oriented. Code is organized around classes, which serve as blueprints for creating objects. Key OOP concepts to master include:
    *   **Classes and Objects:** Defining classes with properties (data) and methods (behavior).
    *   **Encapsulation:** Protecting data within a class and controlling access using access modifiers (`public`, `private`, `protected`).
    *   **Inheritance:** Creating new classes based on existing ones, inheriting their characteristics.
    *   **Polymorphism:** Enabling objects of different classes to respond to the same method call in their own way.
*   **Namespaces: Code Organization:** Namespaces are like Python modules, but on steroids. They provide a hierarchical way to organize code, preventing naming conflicts and grouping related classes. You'll use the `using` keyword to import namespaces and access their contents (e.g., `using System;`).
*   **Methods: Class-Bound Functions:** Methods are functions that belong to a class. They define the actions an object can perform. Pay attention to method signatures, including return types, parameters, and access modifiers. The `static` keyword allows you to define methods that belong to the class itself, rather than to an instance.
*   **Control Flow with Braces:** C# uses curly braces `{}` to define code blocks for control flow statements like `if`, `else`, `for`, `while`, and `switch`. This is a key syntactic difference from Python's indentation-based approach.
*   **Collections: Data Structures:** C# offers a rich set of collection classes for storing and managing data, including arrays, lists (`List<T>`), and dictionaries (`Dictionary<TKey, TValue>`). Choosing the right collection type for your needs is crucial for performance and efficiency.
*   **The .NET Ecosystem:** C# code runs on the .NET runtime. Understanding the basics of the .NET framework, including the Common Language Runtime (CLR) and the Base Class Library (BCL), will provide a deeper understanding of how C# code is executed and the vast library of pre-built functionality available to you.

### Lessons Learned: Key Takeaways for Pythonistas
After converting the Fibonacci sequence and exploring these core concepts, here are the most significant lessons I learned:

*   **Embrace Static Typing:** While it might feel verbose at first, static typing leads to more robust and maintainable code. I need to get comfortable with declaring variable types and understanding how the compiler enforces type safety.
*   **OOP is Fundamental:** C# is an object-oriented language through and through.
*   **Leverage the .NET Framework:** The .NET framework provides a wealth of pre-built classes and methods that can significantly speed up development.
*   **Syntax Matters:** Paying close attention to the syntax, especially the use of curly braces for code blocks, is important. Small syntactic errors can prevent the code from compiling.
*   **AI as a Learning Accelerator:** Using AI tools to generate code and explain concepts can be a powerful way to learn C#. Focusing on understanding the *why* behind the code, rather than just the *how*, is what makes the difference between learning and just letting AI doing everything for you.

### Ending Notes
Converting Python code to C# can seem daunting at first, but by understanding the core concepts and syntax differences, the transition becomes much smoother. This exercise with the Fibonacci sequence highlights the importance of static typing, object-oriented programming, and the structure that namespaces provide in C#. What made this learning experience truly powerful was the use of AI to generate the initial C# code and provide explanations. This approach allowed me to focus on understanding the why behind the code, rather than getting bogged down in syntax errors. While Python offers flexibility and rapid prototyping, C# brings robustness and performance, especially beneficial for larger applications. It's a matter of chosing the right tool for the job. In my opinion, Python is great for quick and small tasks, as well as situations where performance is not a big factor. And, crucially, by using AI as a learning companion, we can accelerate the process of mastering new languages and paradigms, making complex tasks like cross-language translation and concept understanding significantly more accessible.