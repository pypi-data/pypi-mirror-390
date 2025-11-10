from collections import Counter

__all__ = [
    'find_duplicate',
]


def find_duplicate(file_list):
    b = dict(Counter(file_list))
    print([key for key, value in b.items() if value > 1])
    print({key: value for key, value in b.items() if value > 1})
    return b
