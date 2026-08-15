import time
from database import SessionLocal
import models
from algorithms import insertion_sort_count, binary_search_count, linear_search_count


def load_tasks(db, limit):
    tasks = db.query(models.Task).limit(limit).all()
    return [
        {"id": t.id, "title": t.title, "priority": t.priority}
        for t in tasks
    ]


def run_benchmark():
    db = SessionLocal()
    sizes = [10, 500, 3000]
    results = []

    for size in sizes:
        records = load_tasks(db, size)
        n = len(records)

        # Insertion sort comparison count (sorts a copy by title)
        sort_records = [dict(r) for r in records]
        sort_comparisons = insertion_sort_count(sort_records, "title")

        # Binary search: search for the last element's title (guaranteed present)
        target = sort_records[-1]["title"] if sort_records else None
        binary_result = binary_search_count(sort_records, target, "title") if target else {"index": -1, "comparison_count": 0}

        # Linear search: same target, unsorted original records
        linear_result = linear_search_count(records, target, "title") if target else {"index": -1, "comparison_count": 0}

        results.append({
            "size": n,
            "insertion_sort_comparisons": sort_comparisons,
            "binary_search_comparisons": binary_result["comparison_count"],
            "linear_search_comparisons": linear_result["comparison_count"],
        })

    db.close()
    return results


if __name__ == "__main__":
    results = run_benchmark()
    print(f"{'Size':<10}{'Insertion Sort':<20}{'Binary Search':<18}{'Linear Search':<15}")
    for r in results:
        print(f"{r['size']:<10}{r['insertion_sort_comparisons']:<20}{r['binary_search_comparisons']:<18}{r['linear_search_comparisons']:<15}")

    with open("results.txt", "w") as f:
        f.write(f"{'Size':<10}{'Insertion Sort':<20}{'Binary Search':<18}{'Linear Search':<15}\n")
        for r in results:
            f.write(f"{r['size']:<10}{r['insertion_sort_comparisons']:<20}{r['binary_search_comparisons']:<18}{r['linear_search_comparisons']:<15}\n")
    print("\nResults saved to results.txt")