# TaskFlow API

A task management API built with FastAPI and SQLAlchemy.

## Features
- CRUD operations for Projects and Tasks
- Project statistics endpoint (pending/in_progress/completed counts)
- CORS-enabled for frontend integration

## Running locally
1. Create a virtual environment and install dependencies from `requirements.txt`
2. Run `uvicorn main:app --reload`
3. Visit `http://127.0.0.1:8000/docs` for interactive API docs

## Section 2 — Algorithms: Complexity & Benchmark Results

### Time Complexity
- **insertion_sort**: Best case O(n) — already-sorted input, one comparison per element, no shifting. Worst case O(n²) — reverse-sorted input, each element shifts through all previously sorted elements.
- **binary_search**: Best case O(1) — target is the middle element on the first check. Worst case O(log n) — target is found only after repeatedly halving the search space, or is absent.
- **linear_search**: Best case O(1) — target is the first element. Worst case O(n) — target is the last element or absent, requiring a full scan.

### Benchmark Results (measured, not estimated)

| Size | Insertion Sort (comparisons) | Binary Search (comparisons) | Linear Search (comparisons) |
|------|------------------------------|------------------------------|------------------------------|
| 10   | 15                           | 4                             | 9                             |
| 500  | 61,737                       | 9                             | 123                           |
| 3000 | 2,223,787                    | 12                            | 123                           |

### Is sorting-first worth it?

Based on these numbers, sorting the task list before every search is **not** worth it for TaskFlow's actual usage pattern. At 3,000 tasks, insertion sort costs over 2.2 million comparisons — a cost paid on *every single sort request* — while binary search only saves roughly 111 comparisons over linear search (12 vs 123) once the list is already sorted. Given that TaskFlow users list and re-sort their tasks repeatedly throughout the day but add or rename tasks far less often, paying O(n²) to sort before every read is drastically more expensive than just linear-scanning an unsorted list each time. Sorting would only pay off if the list were sorted once and then searched many times *without* being re-sorted or re-fetched — which isn't how the sort endpoint is currently used, since it re-sorts from scratch on every call. A more efficient design would cache the sorted result or use a faster sort (e.g. one with O(n log n) worst case) if sorting-before-search became the dominant access pattern.