r"""Contain functions to manage package versions."""

from __future__ import annotations

__all__ = ["get_latest_major_versions", "get_latest_minor_versions", "get_versions"]

from functools import lru_cache

from ghflowgen.utils.pypi import get_pypi_versions
from ghflowgen.version.filtering import (
    filter_range_versions,
    filter_stable_versions,
    filter_valid_versions,
    latest_major_versions,
    latest_minor_versions,
)


@lru_cache
def get_versions(
    package: str, lower: str | None = None, upper: str | None = None
) -> tuple[str, ...]:
    r"""Get the valid versions for a given package.

    Args:
        package: The package name.
        lower: The lower version bound (inclusive).
            If ``None``, no lower limit is applied.
        upper: The upper version bound (exclusive).
            If None, no upper limit is applied.

    Returns:
        A tuple containing the valid versions.

    Example usage:

    ```pycon

    >>> from ghflowgen.version import get_versions
    >>> versions = get_versions("requests")  # doctest: +SKIP

    ```
    """
    versions = get_pypi_versions(package)
    versions = filter_valid_versions(versions)
    versions = filter_stable_versions(versions)
    return tuple(filter_range_versions(versions, lower=lower, upper=upper))


@lru_cache
def get_latest_major_versions(
    package: str, lower: str | None = None, upper: str | None = None
) -> tuple[str, ...]:
    r"""Get the latest version for each major version for a given
    package.

    Args:
        package: The package name.
        lower: The lower version bound (inclusive).
            If ``None``, no lower limit is applied.
        upper: The upper version bound (exclusive).
            If None, no upper limit is applied.

    Returns:
        A tuple containing the latest version for each major version,
            sorted by major version number.

    Example usage:

    ```pycon

    >>> from ghflowgen.version import get_latest_major_versions
    >>> versions = get_latest_major_versions("requests")  # doctest: +SKIP

    ```
    """
    versions = get_versions(package, lower=lower, upper=upper)
    return tuple(latest_major_versions(versions))


@lru_cache
def get_latest_minor_versions(
    package: str, lower: str | None = None, upper: str | None = None
) -> tuple[str, ...]:
    r"""Get the latest version for each minor version for a given
    package.

    Args:
        package: The package name.
        lower: The lower version bound (inclusive).
            If ``None``, no lower limit is applied.
        upper: The upper version bound (exclusive).
            If None, no upper limit is applied.

    Returns:
        A tuple containing the latest version for each minor version,
            sorted by minor version number.

    Example usage:

    ```pycon

    >>> from ghflowgen.version import get_latest_minor_versions
    >>> versions = get_latest_minor_versions("requests")  # doctest: +SKIP

    ```
    """
    versions = get_versions(package, lower=lower, upper=upper)
    return tuple(latest_minor_versions(versions))
