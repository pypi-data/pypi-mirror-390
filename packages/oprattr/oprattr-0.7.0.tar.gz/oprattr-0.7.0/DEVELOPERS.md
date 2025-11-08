# Developer Notes

This document contains notes for those who wish to contribute to `oprattr` by modifying the code base. In order to develop `oprattr`, you should fork the respository, edit your forked copy, and submit a pull request for integration with the original repository.

Note that this is a living document and is subject to change without notice.

## Version Numbers

When incrementing the version number to X.Y.Z, please do the following
* create a new subsection in `CHANGELOG.md`, below **NEXT**, with the title
  formatted as vX.Y.Z (YYYY-MM-DD)
* update the version number in `pyproject.toml`
* commit with the message "Increment version to X.Y.Z"
* create a tag named "vX.Y.Z" with the message "version X.Y.Z"
* push and follow tags

