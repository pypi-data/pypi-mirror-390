import os
import shutil


def delete_files(path_storage: str, extensions: list[str]) -> None:
    """Delete files with specified extensions from a directory.

    Removes all files in the given directory that have any of the specified
    file extensions. The function processes each file in the directory and
    deletes those matching the extension criteria.

    Args:
        path_storage: Directory path containing files to potentially delete.
        extensions: List of file extensions to match (e.g., ['.txt', '.log']).
                   Extensions should include the dot prefix.

    Returns:
        None: Files are deleted in place, no return value.

    Note:
        This function permanently deletes files. Use with caution.

    Examples:
        >>> delete_files("/tmp", [".txt", ".log"])
        # Deletes all .txt and .log files in /tmp directory
    """
    exts = list(set(extensions))
    for name in os.listdir(path_storage):
        for ext in exts:
            if name.endswith(ext):
                os.remove(os.path.join(path_storage, name))


def delete_empty_lines(data_list: list[str]) -> list[str]:
    """Remove all empty lines from a list of strings.

    Filters out lines that are empty or contain only whitespace characters,
    returning a new list with only non-empty lines.

    Args:
        data_list: List of strings to filter.

    Returns:
        List[str]: New list containing only non-empty lines.

    Examples:
        >>> delete_empty_lines(["hello", "", "world", "   ", "test"])
        ['hello', 'world', 'test']
        >>> delete_empty_lines([])
        []
    """
    return [line for line in data_list if line.strip()]


def delete_empty_lines_first_occur(data_list: list[str]) -> list[str]:
    """Remove empty lines from the beginning of a list.

    Removes consecutive empty lines from the start of the list until the
    first non-empty line is encountered.

    Args:
        data_list: List of strings to process.

    Returns:
        List[str]: List with leading empty lines removed, or empty list
                  if all lines are empty.

    Examples:
        >>> delete_empty_lines_first_occur(["", "", "hello", "world"])
        ['hello', 'world']
        >>> delete_empty_lines_first_occur(["", "", ""])
        []
        >>> delete_empty_lines_first_occur(["hello", "world"])
        ['hello', 'world']
    """
    for i in range(len(data_list)):
        if data_list[i].strip():
            return data_list[i:]
    return []


def delete_empty_lines_last_occur_add_new_line(data_list: list[str]) -> list[str]:
    r"""Remove trailing empty lines and ensure proper newline ending.

    Removes empty lines from the end of the list and ensures the last
    line ends with a newline character.

    Args:
        data_list: List of strings to process.

    Returns:
        List[str]: List with trailing empty lines removed and proper
                  newline ending added to the last line.

    Examples:
        >>> result = delete_empty_lines_last_occur_add_new_line(["hello", "world", "", ""])
        >>> result
        ['hello', 'world\n']
    """
    data_list = delete_empty_lines_first_occur(data_list[::-1])[::-1]
    if data_list:
        data_list[-1] = f"{data_list[-1].rstrip()}\n"
    return data_list


def delete_python_cache(path_root: str) -> None:
    """Recursively delete all __pycache__ directories.

    Walks through the directory tree starting from the given root path
    and removes all __pycache__ directories and their contents.

    Args:
        path_root: Root directory path to start the search from.

    Returns:
        None: __pycache__ directories are deleted in place.

    Note:
        This function permanently deletes directories. Use with caution.

    Examples:
        >>> delete_python_cache("/path/to/project")
        # Removes all __pycache__ directories under /path/to/project
    """
    for root, dirs, _ in os.walk(path_root):
        for folder in dirs:
            if folder == "__pycache__":
                shutil.rmtree(os.path.join(root, folder))


def delete_redundant_elements(element_list: list[str]) -> list[str]:
    """Remove duplicate elements while preserving order.

    Removes duplicate elements from the list while maintaining the original
    order of first occurrence. Also strips whitespace from each element
    and filters out empty elements.

    Args:
        element_list: List of strings to deduplicate.

    Returns:
        List[str]: New list with duplicates removed, whitespace stripped,
                  and empty elements filtered out, preserving original order.

    Examples:
        >>> delete_redundant_elements(["a", "b", "a", "c", " b ", ""])
        ['a', 'b', 'c']
        >>> delete_redundant_elements(["x", "x", "x"])
        ['x']
    """
    new_element_list = [e.strip() for e in element_list if e.strip()]
    return sorted(set(new_element_list), key=new_element_list.index)


if __name__ == "__main__":
    pass
