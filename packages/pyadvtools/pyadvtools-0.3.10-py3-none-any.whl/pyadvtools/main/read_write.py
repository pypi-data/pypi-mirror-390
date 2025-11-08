import os
import platform
import re

from pyadvtools.core.delete import delete_empty_lines_first_occur, delete_empty_lines_last_occur_add_new_line


def is_valid_filename(filename: str) -> bool:
    """Check if a filename is valid for common file systems.

    Validates a filename against common file system restrictions including
    illegal characters, reserved patterns, and naming conventions.
    Cross-platform compatible for Windows, macOS, and Linux.

    Args:
        filename: The filename to validate.

    Returns:
        bool: True if valid, False otherwise.

    Examples:
        >>> is_valid_filename("test.txt")
        True
        >>> is_valid_filename("test")
        False
        >>> is_valid_filename("file<name>.txt")
        False
    """
    # Empty filename check
    if not filename:
        return False

    # Platform-specific illegal characters
    system = platform.system().lower()
    if system == "windows":
        # Windows illegal characters: < > : " | ? * and control characters
        illegal_chars = '<>:"|?*'
        # Also check for control characters (ASCII 0-31)
        if any(ord(char) < 32 for char in filename):
            return False
    else:
        # Unix-like systems: only / and null character
        illegal_chars = "/\0"

    if any(char in filename for char in illegal_chars):
        return False

    # Check for hidden file without actual name (just '.')
    if filename == ".":
        return False

    # Prevent directory traversal attacks
    if ".." in filename:
        return False

    # Check for leading or trailing spaces
    if filename.strip() != filename:
        return False

    # Check for consecutive spaces
    if "  " in filename:
        return False

    # Windows-specific: reserved names
    if system == "windows":
        reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }
        name_without_ext = filename.split(".")[0].upper()
        if name_without_ext in reserved_names:
            return False

    # Require file extension (at least one dot)
    if "." not in filename:
        return False

    return True


def read_list(file_name: str, read_flag: str = "r", path_storage: str | None = None) -> list[str]:
    r"""Read a text file and return its content as a list of lines.

    Reads a text file and returns its content as a list of strings,
    with proper handling of file paths, existence checks, and content
    formatting. Uses Unix-style line endings (\n) consistently across
    all platforms.

    Args:
        file_name: Name of the file to read.
        read_flag: File open mode (default: "r" for read).
        path_storage: Optional directory path to prepend to file_name.

    Returns:
        List[str]: List of file lines with Unix-style line endings (\n),
                  or empty list if file doesn't exist.

    Examples:
        >>> read_list("test.txt")
        ['line1\n', 'line2\n']
        >>> read_list("nonexistent.txt")
        []

    Note:
        This function enforces Unix-style line endings (\n) regardless
        of the host operating system. All line endings are normalized
        to \n during reading.
    """
    # Construct full path if storage directory is provided
    if path_storage is not None:
        file_name = os.path.join(path_storage, file_name)

    # Return empty list if file doesn't exist
    if not os.path.isfile(file_name) or not os.path.exists(file_name):
        return []

    # Read file with UTF-8 encoding and Unix-style line ending handling
    with open(file_name, read_flag, encoding="utf-8", newline="\n") as f:
        # Read all lines preserving line endings
        data_list = f.readlines()

    # Clean up empty lines and ensure proper formatting
    return delete_empty_lines_last_occur_add_new_line(data_list)


def write_list(
    data_list: list[str] | list[bytes],
    file_name: str,
    write_flag: str = "w",
    path_storage: str | None = None,
    check: bool = True,
    delete_first_empty: bool = True,
    delete_last_empty: bool = True,
    compulsory: bool = False,
    delete_original_file: bool = False,
) -> None:
    r"""Write data to a file with comprehensive file handling.

    Writes a list of strings or bytes to a file with extensive options
    for file handling, validation, and content processing. Enforces
    Unix-style line endings (\n) for text files across all platforms.

    Args:
        data_list: List of strings or bytes to write.
        file_name: Target file name.
        write_flag: File open mode ('w', 'a', 'wb', etc.).
        path_storage: Optional directory path for the file.
        check: If True, checks if file exists before overwriting.
        delete_first_empty: Remove empty lines from start of data.
        delete_last_empty: Remove empty lines from end of data.
        compulsory: Write file even if data is empty.
        delete_original_file: Delete existing file if data is empty.

    Returns:
        None: Writes to file or prints error messages.

    Examples:
        >>> write_list(["line1", "line2"], "output.txt")
        # Writes lines to output.txt with Unix-style line endings

    Note:
        - Text files are always written with Unix-style line endings (\n)
          regardless of the host operating system
        - Binary files are written as-is without line ending conversion
        - Empty line removal occurs before line ending normalization
    """
    # Validate filename
    name = os.path.basename(file_name)
    if not is_valid_filename(name):
        print(f"Invalid file name: {name}")
        return None

    # Construct full file path
    full_file_name = os.path.join(path_storage, file_name) if path_storage else file_name
    full_path = os.path.dirname(full_file_name)

    # Handle binary data writing
    if all(isinstance(i, bytes) for i in data_list) and write_flag == "wb":
        # Create directory if needed
        if full_path and not os.path.exists(full_path):
            os.makedirs(full_path)

        # Filter and write binary data
        temp_data_list = [i for i in data_list if isinstance(i, bytes)]
        with open(full_file_name, "wb") as f:
            f.writelines(temp_data_list)

    # Handle text data writing
    else:
        # Validate all items are strings
        if not all(isinstance(i, str) for i in data_list):
            return None

        # Process text data
        new_data_list = [i for i in data_list if isinstance(i, str)]

        # Remove empty lines from start and end
        if delete_last_empty:
            new_data_list = delete_empty_lines_last_occur_add_new_line(new_data_list)
        if delete_first_empty:
            new_data_list = delete_empty_lines_first_occur(new_data_list)

        # Write file if data exists or compulsory flag is set
        if new_data_list or compulsory:
            # Create directory if needed
            if full_path and not os.path.exists(full_path):
                os.makedirs(full_path)

            # Check if file exists and not in append mode
            if not re.search("a", write_flag) and check and os.path.isfile(full_file_name):
                print(f"{full_file_name} already exists and do nothing.")
            else:
                # Write data to file with Unix-style line ending handling
                with open(full_file_name, write_flag, encoding="utf-8", newline="\n") as f:
                    f.writelines(new_data_list)

        # Delete original file if data is empty and flag is set
        elif delete_original_file and os.path.exists(full_file_name):
            os.remove(full_file_name)

    return None


if __name__ == "__main__":
    print(is_valid_filename("test.md"))  # True
    print(is_valid_filename("test"))  # False
