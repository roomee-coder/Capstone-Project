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

## Section 3 — AI Quick-Add: Parser Design & Worked Examples

### Prompting Technique Rationale

The mock parser in `quick_add.py` is modeled on a **zero-shot, rule-based** approach rather than a few-shot or chain-of-thought prompting style, because the parsing task is fully deterministic and specified as an exact algorithm (fixed keyword lists, fixed matching order, fixed stripping rules) rather than an open-ended language understanding problem. A real LLM call using this design would use a single system-role instruction describing the parsing behavior precisely — priority keyword groups, the Monday-to-Sunday date-phrase check order, and the title-stripping steps — with the free-text description as the user-role message, and no worked examples embedded in the prompt itself. This keeps token usage minimal (one instruction, one input, no repeated example pairs) and maximizes reliability, since a rule-based system prompt removes ambiguity that few-shot examples would otherwise need to disambiguate through pattern-matching. Chain-of-thought prompting was intentionally avoided because it would introduce non-determinism: two runs of the same input could produce different intermediate reasoning and, potentially, different final output, which conflicts with the requirement that the mock and any real-LLM implementation produce identical results for identical input. The trade-off is that this approach is less flexible for descriptions using phrasing outside the fixed keyword set — for example, "critical" would not be recognized as high priority — but this is an acceptable trade-off for a task-creation shortcut that favors predictable, testable behavior over broader natural-language coverage.

### Worked Examples

| # | Input `description` | Parsed Output |
|---|---|---|
| 1 | `"This is urgent, mark it ASAP please"` | `{"title": "This is , mark it please", "priority": "high", "due_date_hint": null}` |
| 2 | `"   "` (whitespace only) | `{"title": "Untitled task", "priority": "medium", "due_date_hint": null}` |
| 3 | `"Finish the report next friday, it's urgent"` | `{"title": "Finish the report , it's", "priority": "high", "due_date_hint": "next friday"}` |
| 4 | `"tomorrow review tomorrow"` | `{"title": "review", "priority": "medium", "due_date_hint": "tomorrow"}` |
| 5 | `"Buy groceries whenever, no rush"` | `{"title": "Buy groceries , no rush", "priority": "low", "due_date_hint": null}` |

All five examples were verified directly against the running `parse_task_description` function output (see terminal output in development log), not computed by hand separately.