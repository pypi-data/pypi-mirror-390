import os


def standard_path(p: str) -> str:
    """Standardize and expand a file path.

    Normalizes a file path by expanding user home directory (~) and
    environment variables, and handles edge cases with trailing slashes.
    Cross-platform compatible for Windows, macOS, and Linux.

    Args:
        p: File path string to standardize.

    Returns:
        str: Standardized and expanded file path.

    Examples:
        >>> standard_path("~/Documents/file.txt")
        '/home/user/Documents/file.txt'  # On Unix-like systems
        >>> standard_path("$HOME/file.txt")
        '/home/user/file.txt'  # On Unix-like systems
        >>> standard_path("/path/to/dir/")
        '/path/to/dir'
    """
    import platform

    # Strip whitespace
    p = p.strip()

    # Handle empty path
    if not p:
        return p

    # Handle trailing slash case
    if os.path.basename(p) == "":
        p = os.path.dirname(p)

    # Expand user home directory (~)
    expanded_path = os.path.expanduser(p)

    # Handle environment variables - platform specific
    system = platform.system().lower()
    if system == "windows":
        # Windows uses %VAR% syntax
        expanded_path = os.path.expandvars(expanded_path)
    else:
        # Unix-like systems use $VAR syntax
        expanded_path = os.path.expandvars(expanded_path)

    # Normalize path separators for cross-platform compatibility
    return os.path.normpath(expanded_path)


if __name__ == "__main__":
    pass
