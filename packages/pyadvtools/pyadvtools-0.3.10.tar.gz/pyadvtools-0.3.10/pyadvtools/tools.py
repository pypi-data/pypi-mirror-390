import os
import re
from pathlib import Path

from pyadvtools.core.sort import sort_int_str
from pyadvtools.core.standard import standard_path
from pyadvtools.main.dict import IterateSortDict, IterateUpdateDict
from pyadvtools.main.list import combine_content_in_list
from pyadvtools.main.read_write import read_list


def iterate_obtain_full_file_names(
    path_storage: str,
    extension: str,
    reverse: bool = True,
    is_standard_file_name: bool = True,
    search_year_list: list[str] = [],
) -> list[str]:
    """Recursively retrieve full file paths with specified extension.

    Walks through a directory tree and collects files matching the given
    extension, with optional filtering based on year patterns and sorting.

    Args:
        path_storage: Root directory path to search for files.
        extension: Target file extension to filter (e.g., 'txt', 'csv').
        reverse: If True, sorts files in reverse order; otherwise natural order.
        is_standard_file_name: If True, enables year-based filtering.
        search_year_list: List of years to filter filenames.

    Returns:
        List[str]: List of full file paths matching criteria, sorted accordingly.

    Examples:
        >>> files = iterate_obtain_full_file_names("/path", "txt", True, True, ["2023"])
        # Returns all .txt files from 2023, sorted in reverse order
    """
    # Return empty list if the target directory does not exist
    if not os.path.exists(path_storage):
        return []

    # Compile regex pattern for year filtering if enabled and years are provided
    regex = None
    if is_standard_file_name and search_year_list:
        # Create regex pattern matching any of the specified years, such as AAAI_2020.bib
        regex = re.compile(f'({"|".join(search_year_list)})')

    file_list = []
    # Recursively walk through all directories and subdirectories
    for root, _, files in os.walk(path_storage, topdown=True):
        # Filter files by the target extension (handling double dots edge case)
        files = [f for f in files if f.endswith(f".{extension}".replace("..", "."))]

        # Apply year-based filtering if regex pattern is available
        if regex:
            files = [f for f in files if regex.search(f)]

        # Convert filenames to full paths and add to result list
        file_list.extend([os.path.join(root, f) for f in files])

    # Sort files using natural numeric and string sorting
    file_list = sort_int_str(file_list, reverse=reverse)
    return file_list


def transform_to_data_list(
    original_data: list[str] | str,
    extension: str,
    reverse: bool = False,
    is_standard_file_name: bool = True,
    search_year_list: list[str] = [],
    insert_flag: list[str] | str | None = None,
    before_after: str = "after",
) -> list[str]:
    r"""Transform input data from various formats into a unified list of strings.

    Supports multiple input types including directories, files, raw strings,
    and string lists, returning a consolidated list of text lines.

    Args:
        original_data: Input source - directory path, file path, multi-line
                      string, or list of strings.
        extension: Target file extension to filter when processing directories.
        reverse: Whether to reverse the order of files when reading from directory.
        is_standard_file_name: Whether to use standardized file name processing.
        search_year_list: Optional list of years to filter files by.
        insert_flag: Content to insert between combined data chunks.
        before_after: Insert position relative to existing content.

    Returns:
        List[str]: Consolidated list of text lines from all processed sources.

    Examples:
        >>> transform_to_data_list("/path/to/files", "txt")
        # Returns combined content from all .txt files in directory
        >>> transform_to_data_list("line1\nline2", "txt")
        ['line1\n', 'line2\n']
    """
    # Handle string input (directory path, file path, or multi-line string)
    if isinstance(original_data, str):
        # Process directory input
        if os.path.isdir(original_data):
            # Get all files with target extension from directory
            files = iterate_obtain_full_file_names(
                standard_path(original_data), extension, reverse, is_standard_file_name, search_year_list
            )

            # Read all files and combine their contents
            data_list = combine_content_in_list([read_list(f, "r", None) for f in files], insert_flag, before_after)

        # Process file input (with matching extension or existing file)
        elif original_data.strip().endswith(extension) or os.path.isfile(original_data):
            # Read all lines from the file
            data_list = read_list(original_data, "r", None)

        # Process multi-line string input
        else:
            # Split string into lines while preserving line endings
            data_list = original_data.splitlines(keepends=True)

    # Handle list input (return directly)
    else:
        data_list = original_data
    return data_list


def generate_nested_dict(path_storage: str) -> dict:
    """Generate a nested dictionary structure representing directory hierarchy.

    Recursively walks through a directory tree and constructs a nested
    dictionary that mirrors the folder structure with files organized
    under their respective directories.

    Args:
        path_storage: Root directory path to generate structure from.

    Returns:
        dict: Nested dictionary representing directory hierarchy with sorted file lists.

    Examples:
        >>> generate_nested_dict("/path/to/project")
        {
            'folder1': {
                'subfolder1': ['file1.txt', 'file2.txt'],
                'subfolder2': ['file3.txt']
            },
            'folder2': ['file4.txt']
        }
    """
    # Initialize dictionary to store flat file structure
    files_dict = {}

    # Recursively walk through all directories and subdirectories
    for root, _, files in os.walk(path_storage, topdown=True):
        for file in files:
            # Create relative path key by removing root path prefix
            # Use os.path.normpath for cross-platform path handling
            relative_path = os.path.normpath(os.path.join(root, file))
            relative_to_storage = os.path.relpath(relative_path, path_storage)
            f = "." + os.path.sep + relative_to_storage

            # Group files by their relative directory path
            relative_dir = os.path.relpath(root, path_storage)
            files_dict.setdefault(relative_dir, []).append(f)

    # Sort file lists alphabetically for each directory
    files_dict = {k: sorted(v) for k, v in files_dict.items()}

    # Initialize nested dictionary structure
    nested_dict = {}

    # Convert flat directory structure to nested hierarchy
    for k, v in files_dict.items():
        # Split path into individual directory components
        keys = [k for k in Path(k).parts if k != os.sep]

        # Skip empty paths (root directory case)
        if not keys:
            continue

        # Create nested dictionary structure for current path
        temp_dict = {keys[-1]: v}
        # Build nested structure backwards (from deepest to shallowest level)
        for j in keys[::-1][1:]:
            temp_dict = {j: temp_dict}

        # Merge the temporary nested structure into the main nested dictionary
        nested_dict = IterateUpdateDict().dict_update(nested_dict, temp_dict)

    # Recursively sort the nested dictionary structure
    nested_dict = IterateSortDict().dict_update(nested_dict)
    return nested_dict
