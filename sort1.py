#!/usr/bin/env python3
"""Sort ONE array of integers.

    python3 sort1.py 5 3 8 1 9 2
    python3 sort1.py "[5, 3, 8, 1]"            also "5,3,8,1"
    python3 sort1.py --desc 5 -3 8 1           descending (negative numbers are OK)
    python3 sort1.py --algo bubble 5 3 8 1     bubble | selection | insertion | merge | quick | builtin
    python3 sort1.py                           asks you to type the numbers

Standard library only. The algorithms are written by hand, in case the exam
says "do not use the built-in sort" (sorted() or list.sort()).
"""
import sys


def bubble_sort(nums):
    """Swap neighbours that are in the wrong order, again and again. O(n²)"""
    a = list(nums)  # work on a copy, keep the input unchanged
    for i in range(len(a) - 1):
        swapped = False
        for j in range(len(a) - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:  # no swap in a full pass: already sorted
            break
    return a


def selection_sort(nums):
    """Find the smallest remaining value and move it to the front. O(n²)"""
    a = list(nums)
    for i in range(len(a) - 1):
        smallest = i
        for j in range(i + 1, len(a)):
            if a[j] < a[smallest]:
                smallest = j
        a[i], a[smallest] = a[smallest], a[i]
    return a


def insertion_sort(nums):
    """Insert each value into the sorted part on its left.
    O(n²), but fast for small or almost sorted lists."""
    a = list(nums)
    for i in range(1, len(a)):
        value = a[i]
        j = i - 1
        while j >= 0 and a[j] > value:
            a[j + 1] = a[j]  # shift bigger values one place right
            j -= 1
        a[j + 1] = value
    return a


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


def quick_sort(nums):
    """Pick a pivot, then sort the smaller and the bigger values separately.
    O(n log n) on average."""
    if len(nums) <= 1:
        return list(nums)
    pivot = nums[len(nums) // 2]
    smaller = [x for x in nums if x < pivot]
    equal = [x for x in nums if x == pivot]
    bigger = [x for x in nums if x > pivot]
    return quick_sort(smaller) + equal + quick_sort(bigger)


ALGORITHMS = {
    "bubble": bubble_sort,
    "selection": selection_sort,
    "insertion": insertion_sort,
    "merge": merge_sort,
    "quick": quick_sort,
    "builtin": sorted,  # Python's own sort
}


def main():
    algo, desc, words = "quick", False, []
    # Options are read by hand instead of with argparse, so that negative
    # numbers like -3 or "-3,5" are never mistaken for options.
    args = sys.argv[1:]
    while args:
        arg = args.pop(0)
        if arg == "--desc":
            desc = True
        elif arg == "--algo" and args:
            algo = args.pop(0)
        elif arg.startswith("--algo="):
            algo = arg.split("=", 1)[1]
        elif arg in ("-h", "--help"):
            print(__doc__)
            return
        else:
            words.append(arg)

    if algo not in ALGORITHMS:
        fail(f"unknown algorithm {algo!r}, use one of: {', '.join(ALGORITHMS)}", code=2)
    try:
        nums = read_numbers(words)
    except ValueError as e:
        fail(e)
    if not nums:
        fail("no numbers given")

    result = ALGORITHMS[algo](nums)
    if desc:
        result.reverse()
    order = "descending" if desc else "ascending"
    print("Input :", nums)
    print("Sorted:", result, f"({algo} sort, {order})")


def read_numbers(words):
    """Get the numbers from the arguments, or from the keyboard (stdin) when there are none."""
    if words:
        return parse_numbers(" ".join(words))
    if sys.stdin.isatty():
        try:
            return parse_numbers(input("Enter numbers (e.g. 5 3 8 1): "))
        except EOFError:  # Ctrl+D
            return []
    return parse_numbers(sys.stdin.readline())


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
