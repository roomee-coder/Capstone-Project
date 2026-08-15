def insertion_sort(records, key):
    """
    Sorts a list of dictionaries in place by the value at record[key].
    Standard insertion sort: starts from the second element, compares
    against previous elements, and shifts to insert each one correctly.
    """
    for i in range(1, len(records)):
        current = records[i]
        j = i - 1
        while j >= 0 and records[j][key] > current[key]:
            records[j + 1] = records[j]
            j -= 1
        records[j + 1] = current


def binary_search(sorted_records, target_value, key):
    """
    Searches a list already sorted by key. Returns the index of a
    record whose record[key] == target_value, or -1 if not found.
    """
    low, high = 0, len(sorted_records) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_value = sorted_records[mid][key]
        if mid_value == target_value:
            return mid
        elif mid_value < target_value:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def linear_search(records, target_value, key):
    """
    Baseline: scans every record in order and returns the index of
    the first match, or -1 if not found.
    """
    for i, record in enumerate(records):
        if record[key] == target_value:
            return i
    return -1

def insertion_sort_count(records, key):
    """
    Same logic as insertion_sort, but counts comparisons.
    Sorts in place. Returns only the comparison count (an int).
    """
    comparisons = 0
    for i in range(1, len(records)):
        current = records[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if records[j][key] > current[key]:
                records[j + 1] = records[j]
                j -= 1
            else:
                break
        records[j + 1] = current
    return comparisons


def binary_search_count(sorted_records, target_value, key):
    """
    Same logic as binary_search, but counts comparisons.
    Returns a dict: {"index": ..., "comparison_count": ...}
    """
    comparisons = 0
    low, high = 0, len(sorted_records) - 1
    index = -1
    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        mid_value = sorted_records[mid][key]
        if mid_value == target_value:
            index = mid
            break
        elif mid_value < target_value:
            low = mid + 1
        else:
            high = mid - 1
    return {"index": index, "comparison_count": comparisons}


def linear_search_count(records, target_value, key):
    """
    Same logic as linear_search, but counts comparisons.
    Returns a dict: {"index": ..., "comparison_count": ...}
    """
    comparisons = 0
    index = -1
    for i, record in enumerate(records):
        comparisons += 1
        if record[key] == target_value:
            index = i
            break
    return {"index": index, "comparison_count": comparisons}