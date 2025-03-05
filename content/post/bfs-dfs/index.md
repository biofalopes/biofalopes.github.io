+++
title = "Breadth-First Search (BFS) and Depth-First Search (DFS): A Deep Dive"
description = "Studying Search Algorithms using Python, Part 1"
date = "2025-03-05"
draft = false
toc = false
tags = ["python"]
categories = ["python"]
image = "banner.jpg"
author = "Fabio M. Lopes"
+++

## Breadth-First Search (BFS)
Breadth-First Search (BFS) is a fundamental graph traversal and search algorithm. It systematically explores a graph level by level, starting from a designated *start node*. BFS will explore all paths one step away from the starting point, then all paths two steps away, and so on, ensuring that the shortest path is found first.

### How BFS Works
1. **Initialization:**
   - Start with a *queue* data structure, typically implemented using `collections.deque` in Python for efficient FIFO (First-In, First-Out) operations. The queue initially contains only the *start node*.
   - Maintain a `visited` set (or list) to keep track of nodes that have already been explored to avoid cycles.
   - Optionally, a `parent` dictionary is used to store the predecessor of each visited node, allowing for path reconstruction later.

2. **Iteration:**
   - While the queue is not empty:
     - Dequeue a node from the front of the queue.  This is the node currently being explored.
     - For each *neighbor* of the current node:
       - If the neighbor has not been visited:
         - Mark the neighbor as visited.
         - Enqueue the neighbor.
         - Record the current node as the *parent* of the neighbor (if path reconstruction is needed).

3. **Termination:**
   - The algorithm terminates when the queue is empty, indicating that all reachable nodes from the start node have been explored.
   - If a *target node* is specified, the search can terminate as soon as the target node is dequeued.  The `parent` dictionary can then be used to reconstruct the shortest path from the start node to the target.

### Pros of BFS
*   **Completeness:** BFS is *complete*, meaning that if a path exists between the start node and the target node, BFS *will* find it.
*   **Optimality:** BFS guarantees finding the *shortest path* (in terms of the number of edges) between the start node and the target node in an unweighted graph.
*   **Simplicity:** The algorithm is relatively straightforward to understand and implement.

### Cons of BFS
*   **Memory Consumption:** BFS can consume a significant amount of memory, especially for large graphs.  This is because it stores all the nodes at the current level in the queue. In the worst-case scenario, where the entire graph needs to be traversed, the queue can grow to hold a large fraction of the total number of nodes.
*   **Not Suitable for Weighted Graphs:** BFS is designed for unweighted graphs.  It finds the shortest path based on the number of edges, not the total weight of the edges. For weighted graphs, algorithms like Dijkstra's algorithm are more appropriate.

### Where BFS Excels
*   **Finding Shortest Paths (Unweighted Graphs):** Its primary strength is finding the shortest path in graphs where all edges have the same weight (or no weight).
*   **Connectivity Testing:** Determining if two nodes are connected in a graph.
*   **Web Crawlers:** BFS can be used to crawl web pages, exploring links level by level.
*   **Social Network Analysis:**  Finding the shortest chain of connections between two people in a social network.
*   **GPS Navigation:** In scenarios where minimizing the number of "hops" is more important than the total distance (e.g., minimizing the number of transfers in public transportation).

### Where BFS Fails
*   **Weighted Graphs:** As mentioned earlier, BFS is not suitable for finding the shortest path in graphs where edges have different weights.
*   **Very Large Graphs:**  The memory requirements of BFS can become prohibitive for very large graphs.
*   **Graphs with High Branching Factors:**  Graphs where each node has many neighbors can lead to a large queue and high memory consumption.

### Common Use Cases
*   **Pathfinding in Games:** Finding the shortest path for a character to move in a game environment (where all moves have the same cost).
*   **Network Routing:** Discovering network topology and finding the shortest paths between devices.
*   **Garbage Collection:**  Tracing reachable objects in memory to identify those that can be safely deallocated.
*   **Peer-to-Peer Networks:** Finding the closest peers in a peer-to-peer network.

## Depth-First Search (DFS)
Depth-First Search (DFS) is another fundamental graph traversal and search algorithm. Instead of exploring a graph level by level like BFS, DFS explores as deeply as possible along each branch before backtracking. DFS will pick a path and follow it to the end, then backtrack to the last branching point and try a different path.

### How DFS Works
1.  **Initialization:**
    *   Start with a *stack* data structure, typically implemented using a Python list.  The stack initially contains only the *start node*.
    *   Maintain a `visited` set (or list) to keep track of nodes that have already been explored to avoid cycles.
    *   Optionally, a `parent` dictionary is used to store the predecessor of each visited node, allowing for path reconstruction later.

2.  **Iteration:**
    *   While the stack is not empty:
        *   Pop a node from the *top* of the stack. This is the node currently being explored.
        *   If the node has not been visited:
            *   Mark the node as visited.
            *   For each *neighbor* of the current node:
                *   If the neighbor has not been visited:
                    *   Push the neighbor onto the *top* of the stack.
                    *   Record the current node as the *parent* of the neighbor (if path reconstruction is needed).

3.  **Termination:**
    *   The algorithm terminates when the stack is empty, indicating that all reachable nodes from the start node have been explored.
    *   If a *target node* is specified, the search can terminate as soon as the target node is popped from the stack and found to be the target. The `parent` dictionary can then be used to reconstruct a path (not necessarily the shortest) from the start node to the target.

### Pros of DFS
*   **Memory Efficiency:** DFS generally requires less memory than BFS, especially for deep graphs.  It only needs to store the nodes on the current path being explored, rather than all the nodes at the current level (as BFS does).
*   **Simple Implementation:** DFS can be implemented recursively, making the code very concise (though the iterative version, using a stack, is also straightforward).
*   **Good for Finding *Any* Path:** If you just need to find *a* path between two nodes (not necessarily the shortest), DFS can be faster than BFS.

### Cons of DFS
*   **Not Guaranteed to Find Shortest Path:** DFS does *not* guarantee finding the shortest path. It finds a path, but that path might be much longer than the shortest path.
*   **Can Get Stuck in Infinite Loops:** If the graph contains cycles and the `visited` set is not used correctly, DFS can get stuck in an infinite loop, exploring the same nodes over and over.
*   **May Explore Irrelevant Paths:** DFS can explore paths that are far away from the target node before finding the target.

### Where DFS Excels
*   **Detecting Cycles:** DFS is well-suited for detecting cycles in a graph. If, during the traversal, you encounter a node that has already been visited (and is still on the stack), it indicates the presence of a cycle.
*   **Topological Sorting:** DFS is used in algorithms for topological sorting of directed acyclic graphs (DAGs).
*   **Path Existence Checking:** Determining if a path exists between two nodes, even if the shortest path is not required.
*   **Solving Puzzles:** DFS can be used to explore possible solutions in puzzles and games (e.g., solving a maze, finding a solution to a Sudoku puzzle).

### Where DFS Fails
*   **Finding Shortest Paths:** When the shortest path is required, BFS or other algorithms like Dijkstra's algorithm are better choices.
*   **Graphs with Long Paths:** In graphs with very long paths, DFS might take a long time to find the target node or explore the entire graph.
*   **Infinite Graphs:** DFS can get lost in infinite graphs if there is no clear termination condition.

### Common Use Cases
*   **Cycle Detection:** As mentioned earlier, DFS is commonly used to detect cycles in graphs.
*   **Topological Sort:** Ordering tasks in a project based on dependencies.
*   **Maze Solving:** Finding a path from the entrance to the exit.
*   **Backtracking Algorithms:** Solving problems where you need to explore different possibilities and backtrack when a dead end is reached (e.g., solving constraint satisfaction problems).
*   **Game AI:** Implementing AI for games where the AI needs to explore possible moves and evaluate their consequences.

I added below two examples, one for BFS and another for DFS:

<details>
<summary><b>BFS Example</b> (Click to Show/Hide)</summary>
from collections import deque
import networkx as nx
import matplotlib.pyplot as plt

def breadth_first_search(graph, start_node, target_node=None):
    visited_nodes = []
    queue = deque([start_node])
    visited_nodes.append(start_node)
    parent = {}

    if start_node not in graph:
        return visited_nodes, None

    if target_node:
      found = False

    while queue:
        node = queue.popleft()

        if target_node and node == target_node:
            found = True
            break

        neighbors = graph.get(node, [])
        for neighbor in neighbors:
            if neighbor not in visited_nodes:
                visited_nodes.append(neighbor)
                queue.append(neighbor)
                parent[neighbor] = node 

    path = None
    if target_node:
        if found:
            path = []
            current = target_node
            while current != start_node:
                path.append(current)
                current = parent[current]
            path.append(start_node)
            path = path[::-1]
    return visited_nodes, path

def plot_graph(graph, node_color='skyblue', edge_color='gray', node_size=500, font_size=12, title="Graph Visualization"):
    G = nx.Graph(graph)
    pos = nx.spring_layout(G)

    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(G, pos, node_color=node_color, node_size=node_size)
    nx.draw_networkx_edges(G, pos, edge_color=edge_color)
    nx.draw_networkx_labels(G, pos, font_size=font_size, font_family="sans-serif")

    plt.title(title)
    plt.axis("off")
    plt.show()

if __name__ == '__main__':
    graph = {
        'A': ['B', 'G'],
        'B': ['C', 'D', 'E'],
        'C': [],
        'D': [],
        'E': ['F', 'I'],
        'F': [],
        'G': ['H', 'J'],
        'H': ['I'],
        'I': [],
        'J': [],
    }

    start_node = 'A'
    target_node = 'F'

    visited, path = breadth_first_search(graph, start_node, target_node)

    print(f"Sequence of visited nodes: {visited}")
    if path:
        print(f"Shortest path from {start_node} to {target_node}: {path}")
    elif not target_node:
        print(f"Target was not specified.")
    else:
        print(f"No path found from {start_node} to {target_node}.")

    plot_graph(graph)
</details>

<details>
<summary><b>DFS Example</b> (Click to Show/Hide)</summary>
from collections import deque
import networkx as nx
import matplotlib.pyplot as plt

def depth_first_search(graph, start_node, target_node=None):
    visited_nodes = []
    stack = [start_node]
    parent = {}

    if start_node not in graph:
        return visited_nodes, None

    if target_node:
      found = False

    while stack:
        node = stack.pop()

        if node not in visited_nodes:
            visited_nodes.append(node)

            if target_node and node == target_node:
                found = True
                break

            neighbors = graph.get(node, [])
            for neighbor in neighbors:
                if neighbor not in visited_nodes:
                    stack.append(neighbor)
                    parent[neighbor] = node

    path = None
    if target_node:
        if found:
            path = []
            current = target_node
            while current != start_node:
                path.append(current)
                current = parent[current]
            path.append(start_node)
            path = path[::-1]
    return visited_nodes, path

def plot_graph(graph, node_color='skyblue', edge_color='gray', node_size=500, font_size=12, title="Graph Visualization"):
    G = nx.Graph(graph)
    pos = nx.spring_layout(G)

    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(G, pos, node_color=node_color, node_size=node_size)
    nx.draw_networkx_edges(G, pos, edge_color=edge_color)
    nx.draw_networkx_labels(G, pos, font_size=font_size, font_family="sans-serif")

    plt.title(title)
    plt.axis("off")
    plt.show()

if __name__ == '__main__':
    graph = {
        'A': ['B', 'G'],
        'B': ['C', 'D', 'E'],
        'C': [],
        'D': [],
        'E': ['F', 'I'],
        'F': [],
        'G': ['H', 'J'],
        'H': ['I'],
        'I': [],
        'J': [],
    }

    start_node = 'A'
    target_node = 'F'

    visited, path = depth_first_search(graph, start_node, target_node)

    print(f"Sequence of visited nodes: {visited}")
    if path:
        print(f"Shortest path from {start_node} to {target_node}: {path}")
    elif not target_node:
        print(f"Target was not specified.")
    else:
        print(f"No path found from {start_node} to {target_node}.")

    plot_graph(graph)
</details>
