# Greedy Algorithms

A **greedy algorithm** builds a solution step‑by‑step, always choosing the locally optimal choice at each step with the hope that these choices lead to a globally optimal solution.

## Core Idea
* **Local optimum → global optimum** (when the problem satisfies *greedy‑choice* and *optimal‑substructure* properties).
* **Iterative selection**: pick the best immediate option, then restrict the remaining problem.
* No backtracking: once an item is chosen it is never reconsidered.

## When Greedy Works
| Problem | Greedy Choice | Result |
|---------|---------------|--------|
| **Activity Selection** | Choose the activity that finishes earliest | Max number of non‑overlapping activities |
| **Interval Scheduling** | Pick the shortest interval | Minimize total time |
| **Huffman Coding** | Merge two least‑probable symbols | Optimal prefix code |
| **Kruskals & Prim’s MST** | Add lightest edge that doesn’t form a cycle | Minimum spanning tree |
| **Dijkstra’s SSSP** | Pick the vertex with smallest known distance | Shortest path (with non‑negative weights) |
| **Fractional Knapsack** | Pick item with highest value/weight | Maximal value |
| **Coin Change (canonical systems)** | Use the largest denomination ≤ remaining amount | Minimal coin count (when system is canonical) |

## Strengths
* **Simplicity** – often a few lines of code.
* **Efficiency** – runs in \(O(n \log n)\) or linear time for many problems.
* **Deterministic** – no randomization or complex state tracking.

## Weaknesses
* **No guarantee** of optimality for all problems.
* Requires a problem to satisfy the greedy‑choice property; otherwise may get a sub‑optimal solution.
* Often fails on *non‑canonical* coin systems or when future constraints influence current choices.

## Practical Tips
1. **Proof of optimality**: Use exchange argument or induction to show greedy choice leads to an optimal solution.
2. **Problem reduction**: Transform the problem into a canonical form where greedy works (e.g., sorting by finish times for scheduling).
3. **Data structures**: Priority queues (heaps) speed up selection of minimum/maximum elements.
4. **Check assumptions**: Ensure edge weights are non‑negative for Dijkstra, or that denominations are canonical for coin change.

## Example – Activity Selection
```
sort activities by finish time
start = 0
for each activity (s, f) in sorted list:
    if s >= start:
        select activity
        start = f
```
This yields the maximum number of non‑overlapping activities.

---

Greedy algorithms are a cornerstone of algorithm design, offering elegant, fast solutions for a wide range of optimization problems when the problem structure supports them.

---
**Sources**
