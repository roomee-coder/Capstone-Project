from algorithms import (
    insertion_sort,
    binary_search,
    linear_search,
    insertion_sort_count,
    binary_search_count,
    linear_search_count,
)


def check(case_name, result, expected):
    if result == expected:
        print(f"PASS: {case_name}")
    else:
        print(f"FAIL: {case_name} — expected {expected}, got {result}")


# 1. insertion_sort on empty list
records = []
insertion_sort(records, "value")
check("insertion_sort empty list", records, [])

# 2. insertion_sort on single-element list
records = [{"value": 5}]
insertion_sort(records, "value")
check("insertion_sort single element", records, [{"value": 5}])

# 3. binary_search finds value at first index
sorted_list = [{"key": i} for i in [1, 2, 3, 4, 5]]
result = binary_search(sorted_list, 1, "key")
check("binary_search first index", result, 0)

# 4. binary_search finds value at last index
result = binary_search(sorted_list, 5, "key")
check("binary_search last index", result, 4)

# 5. binary_search finds value at middle index
result = binary_search(sorted_list, 3, "key")
check("binary_search middle index", result, 2)

# 6. binary_search returns not-found result when absent
result = binary_search(sorted_list, 99, "key")
check("binary_search not found", result, -1)

# 7. insertion_sort_count on small hand-checkable list
records = [{"key": 3}, {"key": 1}, {"key": 2}]
count = insertion_sort_count(records, "key")
sorted_correctly = records == [{"key": 1}, {"key": 2}, {"key": 3}]
count_is_valid_int = isinstance(count, int) and count > 0
check("insertion_sort_count sorts list correctly", sorted_correctly, True)
check("insertion_sort_count returns positive int", count_is_valid_int, True)

# 8. binary_search_count on sorted list, value present at known index
sorted_list = [{"key": i} for i in [10, 20, 30, 40, 50]]
result = binary_search_count(sorted_list, 30, "key")
index_correct = result["index"] == 2
count_valid = isinstance(result["comparison_count"], int) and result["comparison_count"] > 0
check("binary_search_count index correct", index_correct, True)
check("binary_search_count comparison_count valid", count_valid, True)

# 9. linear_search_count on list for absent value
records = [{"key": 1}, {"key": 2}, {"key": 3}]
result = linear_search_count(records, 99, "key")
index_correct = result["index"] == -1
count_correct = result["comparison_count"] == len(records)
check("linear_search_count not-found index", index_correct, True)
check("linear_search_count comparison_count equals list length", count_correct, True)

print("\nAll checks complete.")