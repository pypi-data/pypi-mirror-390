from typing import List


def list_duplicates(origin: list) -> List:
    result = []
    seen = set()
    for item in origin:
        if item in seen:
            result.append(item)
        else:
            seen.add(item)
    return result
