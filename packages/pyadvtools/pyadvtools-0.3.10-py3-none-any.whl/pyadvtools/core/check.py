from typing import Any


def is_empty(x: Any) -> bool:
    """Check whether the input is empty.

    Determines if the input value is considered empty based on various criteria:
        - Empty strings (after stripping whitespace)
        - Collections with zero length (lists, dicts, tuples)
        - None values
        - False boolean values

    Args:
        x: The value to check for emptiness. Can be any type.

    Returns:
        bool: True if the input is considered empty, False otherwise.

    Examples:
        >>> is_empty("")
        True
        >>> is_empty("   ")
        True
        >>> is_empty([])
        True
        >>> is_empty({})
        True
        >>> is_empty(None)
        True
        >>> is_empty(False)
        True
        >>> is_empty("hello")
        False
        >>> is_empty([1, 2, 3])
        False
    """
    if (isinstance(x, str) and (len(x.strip()) == 0)) or (len(x) == 0) or (x is None) or (x is False):
        return True
    return False


def is_list_contain_str(xx: list) -> bool:
    """Check if all elements in the list are strings.

    Verifies that every element in the provided list is of string type.

    Args:
        xx: List of elements to check for string type.

    Returns:
        bool: True if all elements are strings, False otherwise.

    Examples:
        >>> is_list_contain_str(["hello", "world", "test"])
        True
        >>> is_list_contain_str(["hello", 123, "world"])
        False
        >>> is_list_contain_str([])
        True
    """
    return all(isinstance(x, str) for x in xx)


def is_list_contain_list_contain_str(xxx: list) -> bool:
    """Check if all nested lists contain only strings.

    Verifies that the input is a list of lists, where each inner list
    contains only string elements.

    Args:
        xxx: List of lists to check for string-only content.

    Returns:
        bool: True if all nested lists contain only strings, False otherwise.

    Examples:
        >>> is_list_contain_list_contain_str([["a", "b"], ["c", "d"]])
        True
        >>> is_list_contain_list_contain_str([["a", "b"], ["c", 123]])
        False
        >>> is_list_contain_list_contain_str([])
        True
    """
    return all(is_list_contain_str(xx) for xx in xxx)


if __name__ == "__main__":
    pass
