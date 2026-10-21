#!/usr/bin/env python3
"""Sort TWO arrays of integers, then merge and compare them.

    python3 sort2.py "5,3,9,1" "8,2,3,7"
    python3 sort2.py "[5, 3, 9]" "[8, 2, 3]"
    python3 sort2.py --desc "5 -3 9" "8 2 3"    descending (negative numbers are OK)
    python3 sort2.py                            asks you to type the two arrays

Standard library only, no built-in sort: merge sort is written by hand.
Its merge() step is exactly "merge two sorted arrays into one".
"""
import sys


def main():
    desc = False
    arrays = []
    for arg in sys.argv[1:]:  # read options by hand, so "-3,2" is an array, not an option
        if arg == "--desc":
            desc = True
        elif arg in ("-h", "--help"):
            print(__doc__)
            return
        else:
            arrays.append(arg)

    if len(arrays) == 2:
        text_a, text_b = arrays
    elif not arrays:  # no arguments: ask for the two arrays
        text_a = ask("Array A (e.g. 5 3 9): ")
        text_b = ask("Array B (e.g. 8 2 3): ")
    else:
        fail('give 2 arrays, each one in quotes, e.g. sort2.py "5,3,9" "8,2,3"', code=2)

    a = parse_or_fail(text_a, "array A")
    b = parse_or_fail(text_b, "array B")

    sorted_a = merge_sort(a)  # with the built-in sort: sorted(a)
    sorted_b = merge_sort(b)
    merged = merge(sorted_a, sorted_b)         # two sorted lists -> one sorted list, O(n+m)
    union = unique(merged)                     # with built-ins: sorted(set(a) | set(b))
    common = intersection(sorted_a, sorted_b)  # with built-ins: sorted(set(a) & set(b))
    if desc:
        for values in (sorted_a, sorted_b, merged, union, common):
            values.reverse()

    print("Array A         :", a)
    print("Array B         :", b)
    print("A sorted        :", sorted_a)
    print("B sorted        :", sorted_b)
    print("Merged A + B    :", merged)
    print("Union (unique)  :", union)
    print("In both A and B :", common)


def merge_sort(nums):
    """Split in two halves, sort each half, merge the two sorted halves. O(n log n)"""
    if len(nums) <= 1:
        return list(nums)
    mid = len(nums) // 2
    return merge(merge_sort(nums[:mid]), merge_sort(nums[mid:]))


def merge(left, right):
    """Join two SORTED lists into one sorted list (two pointers)."""
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    return out + left[i:] + right[j:]  # add what is left (only one of them is not empty)


def unique(sorted_nums):
    """Remove duplicates from a SORTED list: [1, 2, 2, 3] -> [1, 2, 3]."""
    out = []
    for x in sorted_nums:
        if not out or out[-1] != x:
            out.append(x)
    return out


def intersection(a, b):
    """Values that are in BOTH sorted lists (no duplicates), with two pointers."""
    out = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            i += 1
        elif a[i] > b[j]:
            j += 1
        else:  # same value in both
            if not out or out[-1] != a[i]:
                out.append(a[i])
            i += 1
            j += 1
    return out


def ask(question):
    """Ask a question (only when a person is typing) and read one line."""
    if sys.stdin.isatty():
        try:
            return input(question)
        except EOFError:  # Ctrl+D
            return ""
    return sys.stdin.readline()


def parse_or_fail(text, name):
    try:
        return parse_numbers(text)
    except ValueError as e:
        fail(f"{name}: {e}")


def parse_numbers(text):
    """Turn "5 3 1", "5,3,1" or "[5, 3, -1]" into a list of ints."""
    for ch in "[],;":
        text = text.replace(ch, " ")
    nums = []
    for word in text.split():
        try:
            nums.append(int(word))
        except ValueError:
            raise ValueError(f"{word!r} is not a whole number") from None
    return nums


def fail(message, code=1):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


if __name__ == "__main__":
    main()
