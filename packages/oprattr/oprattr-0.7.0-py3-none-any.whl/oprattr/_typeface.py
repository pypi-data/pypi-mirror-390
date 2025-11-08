"""
Support for type annotations.

This module provides a single interface to type annotations, including those
that are not defined by the operative Python version and those that this package
prefers to use from future versions.

Examples
--------
* Suppose `BestType` is available in the `typing` module starting with Python
  version 3.X and is available in the `typing_extensions` module for earlier
  versions. If the user is running with Python version <3.X, this module will
  import `BestType` from `typing_extensions`. Otherwise, it will import
  `BestType` from `typing`.
* Support `UpdatedType` is available in the `typing` module for the user's
  version of Python, but this package wishes to take advantage of updates since
  that version. This module will automatically import the version from
  `typing_extensions`.
"""

import typing
import typing_extensions


__all__ = ()

EXTENDED = [
    'Protocol',
]

def __getattr__(name: str) -> type:
    """Get a built-in type annotation."""
    if name in EXTENDED:
        return getattr(typing_extensions, name)
    try:
        attr = getattr(typing, name)
    except AttributeError:
        attr = getattr(typing_extensions, name)
    return attr



