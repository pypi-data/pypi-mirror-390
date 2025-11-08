import re

from pyadvtools.core.check import is_list_contain_list_contain_str, is_list_contain_str


def combine_content_in_list(
    data_list: list[str] | list[list[str]],
    insert_flag: list[str] | str | None = None,
    before_after: str = "after",
) -> list[str]:
    """Combine content in list with optional insertion flags.

    Combines content from a list of strings or list of string lists,
    optionally inserting flags between each item.

    Args:
        data_list: List of strings or list of string lists to combine.
        insert_flag: Content to insert between items. Can be a string,
                    list of strings, or None for no insertion.
        before_after: Position to insert flag - "before" or "after" each item.

    Returns:
        List[str]: Combined list with optional insertions.

    Examples:
        >>> combine_content_in_list(["a", "b"], "---")
        ['a', '---', 'b', '---']
        >>> combine_content_in_list([["a", "b"], ["c", "d"]], "---")
        ['a', 'b', '---', 'c', 'd', '---']
    """
    if before_after not in ["after", "before"]:
        before_after = "after"

    if insert_flag is None:
        insert_flag = []
    elif isinstance(insert_flag, str):
        insert_flag = [insert_flag]

    new_list = []
    if is_list_contain_str(data_list):
        for line in data_list:
            if isinstance(line, str):
                if before_after == "after":
                    new_list.append(line)
                    new_list.extend(insert_flag)
                else:
                    new_list.extend(insert_flag)
                    new_list.extend(line)

    elif is_list_contain_list_contain_str(data_list):
        for line in data_list:
            if isinstance(line, list):
                if before_after == "after":
                    new_list.extend(line)
                    new_list.extend(insert_flag)
                else:
                    new_list.extend(insert_flag)
                    new_list.extend(line)
    else:
        pass
    return new_list


def insert_list_in_list(
    data_list: list[str],
    insert_content_list: list[str],
    insert_flag: int | str,
    insert_before_after: str = "after",
    insert_times: float = 1,
) -> list[str]:
    """Insert content into a list at specified positions.

    Inserts a list of content into another list either at a specific index
    or at positions matching a regex pattern.

    Args:
        data_list: List to insert content into.
        insert_content_list: Content to insert.
        insert_flag: Position indicator - integer index or regex pattern.
        insert_before_after: "before" or "after" the target position.
        insert_times: Number of times to perform insertion (for regex).

    Returns:
        List[str]: New list with content inserted.

    Examples:
        >>> insert_list_in_list(["a", "b", "c"], ["X", "Y"], 2)
        ['a', 'b', 'X', 'Y', 'c']
        >>> insert_list_in_list(["a", "b", "c"], ["X"], "b", "before")
        ['a', 'X', 'b', 'c']
    """
    new_list = []

    if isinstance(insert_flag, int):
        if insert_flag < len(data_list):
            new_list.extend(data_list[: (insert_flag - 1)])  # the insert_flag in th line
            if insert_before_after == "before":
                new_list.extend(insert_content_list)
                new_list.append(data_list[insert_flag - 1])
            elif insert_before_after == "after":
                new_list.append(data_list[insert_flag - 1])
                new_list.extend(insert_content_list)
            new_list.extend(data_list[insert_flag:])
        else:
            new_list = data_list

    elif isinstance(insert_flag, str):
        cnt = 0
        for line in data_list:
            if cnt < insert_times and re.search(insert_flag, line):
                cnt += 1
                if insert_before_after == "before":
                    new_list.extend(insert_content_list)
                    new_list.append(line)
                elif insert_before_after == "after":
                    new_list.append(line)
                    new_list.extend(insert_content_list)
            else:
                new_list.append(line)
    return new_list


def pairwise_combine_in_list(
    data_list_list_one: list[list[str]], data_list_list_two: list[list[str]], mid_flag: str | list = "\n"
) -> list[list[str]]:
    """Pairwise combine two lists of lists.

    Combines corresponding lists from two list-of-lists structures.
    The lists must have the same length.

    Args:
        data_list_list_one: First list of lists to combine.
        data_list_list_two: Second list of lists to combine.
        mid_flag: Content to insert between combined lists.

    Returns:
        List[List[str]]: List of combined lists, or empty list if lengths don't match.

    Examples:
        >>> pairwise_combine_in_list([["a"], ["b"]], [["c"], ["d"]])
        [['a', 'c'], ['b', 'd']]
    """
    if len(data_list_list_one) == 0:
        return data_list_list_two
    if len(data_list_list_two) == 0:
        return data_list_list_one
    if len(data_list_list_one) != len(data_list_list_two):
        print("The length of the two inputs should be equal.")
        return []

    if isinstance(mid_flag, str):
        mid_flag = [mid_flag]

    new_list_list = []
    for i, j in zip(data_list_list_one, data_list_list_two, strict=True):
        new_list = []
        new_list.extend(i)
        new_list.extend(j)
        new_list_list.append(new_list)
    return new_list_list


def substitute_in_list(old_list: list[str], new_list: list[str], data_list: list[str]) -> list[str]:
    """Substitute patterns in list elements.

    Performs regex substitutions on each element of a list, replacing
    patterns from old_list with corresponding patterns from new_list.

    Args:
        old_list: List of regex patterns to find.
        new_list: List of replacement patterns (must match old_list length).
        data_list: List of strings to perform substitutions on.

    Returns:
        List[str]: List with substitutions applied, or original list if
                  old_list and new_list lengths don't match.

    Examples:
        >>> substitute_in_list(["old"], ["new"], ["old text", "another old"])
        ['new text', 'another new']
    """
    if len(old_list) != len(new_list):
        print(f"The lengths of {old_list} and {new_list} should be equal.")
        return data_list

    new_data_list = []
    for line in data_list:
        for i, j in zip(old_list, new_list, strict=True):
            line = re.sub(i, j, line)
        new_data_list.append(line)
    return new_data_list


if __name__ == "__main__":
    pass
