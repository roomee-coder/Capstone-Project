import re

PRIORITY_HIGH_KEYWORDS = ["urgent", "asap"]
PRIORITY_LOW_KEYWORDS = ["whenever", "low priority"]
WEEKDAYS_IN_ORDER = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def parse_task_description(description):
    text_lower = description.lower()

    # --- Priority ---
    has_high_keyword = any(kw in text_lower for kw in PRIORITY_HIGH_KEYWORDS)
    has_low_keyword = any(kw in text_lower for kw in PRIORITY_LOW_KEYWORDS)

    if has_high_keyword:
        priority = "high"
    elif has_low_keyword:
        priority = "low"
    else:
        priority = "medium"

    # --- Due-date hint ---
    due_date_hint = None
    if "today" in text_lower:
        due_date_hint = "today"
    elif "tomorrow" in text_lower:
        due_date_hint = "tomorrow"
    elif "next week" in text_lower:
        due_date_hint = "next week"
    else:
        matched_next_phrase = None
        for day in WEEKDAYS_IN_ORDER:
            phrase = f"next {day}"
            if phrase in text_lower:
                matched_next_phrase = phrase
                break
        if matched_next_phrase:
            due_date_hint = matched_next_phrase
        else:
            for day in WEEKDAYS_IN_ORDER:
                if day in text_lower:
                    due_date_hint = day
                    break

    # --- Title: strip every occurrence of every matched keyword/phrase ---
    title = description
    keywords_to_strip = PRIORITY_HIGH_KEYWORDS + PRIORITY_LOW_KEYWORDS
    for kw in keywords_to_strip:
        title = re.sub(re.escape(kw), "", title, flags=re.IGNORECASE)
    if due_date_hint:
        title = re.sub(re.escape(due_date_hint), "", title, flags=re.IGNORECASE)

    title = re.sub(r"\s+", " ", title).strip()
    if title == "":
        title = "Untitled task"

    return {
        "title": title,
        "priority": priority,
        "due_date_hint": due_date_hint,
    }