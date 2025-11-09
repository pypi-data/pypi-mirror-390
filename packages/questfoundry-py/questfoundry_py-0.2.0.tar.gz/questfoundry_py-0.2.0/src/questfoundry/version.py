"""Version information for QuestFoundry-Py."""

__version__ = "0.2.0"
__version_info__ = (0, 1, 0)


def get_version() -> str:
    """Get the version string.

    Returns:
        The version string in MAJOR.MINOR.PATCH format.

    Example:
        >>> get_version()
        '0.1.0'
    """
    return __version__
