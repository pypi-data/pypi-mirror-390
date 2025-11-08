import re


def arg_sorted(elements: list, reverse: bool = False) -> list[int]:
    """Return indices that would sort the list.

    Returns the indices of elements in the order they would appear
    if the list were sorted, without actually sorting the original list.

    Args:
        elements: List of elements to get sort indices for.
        reverse: If True, returns indices for descending order.

    Returns:
        List[int]: List of indices in sort order.

    Examples:
        >>> arg_sorted([3, 1, 4, 1, 5])
        [1, 3, 0, 2, 4]
        >>> arg_sorted([3, 1, 4, 1, 5], reverse=True)
        [4, 2, 0, 1, 3]
    """
    return sorted(range(len(elements)), key=lambda k: elements[k], reverse=reverse)


def sort_strings_with_embedded_numbers(s: str) -> list[str]:
    """Split string into parts for natural sorting with embedded numbers.

    Splits a string into alternating text and numeric parts, converting
    numeric parts to integers for proper natural sorting.

    Args:
        s: String to split into sortable parts.

    Returns:
        List[str]: List of alternating text and integer parts.

    Examples:
        >>> sort_strings_with_embedded_numbers("abc123def456")
        ['abc', 123, 'def', 456]
        >>> sort_strings_with_embedded_numbers("file10.txt")
        ['file', 10, '.txt']
    """
    re_digits = re.compile(r"(\d+)")
    pieces = re_digits.split(s)
    pieces[1::2] = map(int, pieces[1::2])
    return pieces


def sort_int_str(str_int: list[str], reverse: bool = False) -> list[str]:
    """Sort strings with natural numeric ordering.

    Sorts a list of strings using natural ordering where embedded numbers
    are sorted numerically rather than lexicographically.

    Args:
        str_int: List of strings to sort.
        reverse: If True, sorts in descending order.

    Returns:
        List[str]: New list with strings sorted using natural ordering.

    Examples:
        >>> sort_int_str(["file1.txt", "file10.txt", "file2.txt"])
        ['file1.txt', 'file2.txt', 'file10.txt']
        >>> sort_int_str(["abc9", "abc12", "abc100"])
        ['abc9', 'abc12', 'abc100']
    """
    return sorted(str_int, key=sort_strings_with_embedded_numbers, reverse=reverse)


def arg_sort_int_str(str_int: list[str], reverse: bool = False) -> list[int]:
    """Return indices for natural sorting of strings with embedded numbers.

    Returns the indices of strings in the order they would appear
    if sorted using natural ordering (numeric parts sorted numerically).

    Args:
        str_int: List of strings to get sort indices for.
        reverse: If True, returns indices for descending order.

    Returns:
        List[int]: List of indices in natural sort order.

    Examples:
        >>> arg_sort_int_str(["file1.txt", "file10.txt", "file2.txt"])
        [0, 2, 1]
        >>> arg_sort_int_str(["abc9", "abc12", "abc100"])
        [0, 1, 2]
    """
    new_str_int = sort_int_str(str_int, reverse=reverse)
    idx = []
    for i in new_str_int:
        for j in range(len(str_int)):
            if (j not in idx) and (i == str_int[j]):
                idx.append(j)
                break
    return idx


if __name__ == "__main__":
    a = ["abc12.txt", "abc9.txt", "abc99.txt", "abc100.txt", "aaa999.txt", "234.bat", "detail.bat"]
    aa = sort_int_str(a)
    print("                :", a)
    print("sorted          :", sorted(a))
    print("arg_sorted      :", arg_sorted(a))
    print("sort_int_str    :", sort_int_str(a))
    print("arg_sort_int_str:", arg_sort_int_str(a))
