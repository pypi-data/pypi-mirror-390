"""
Utilities Library

A comprehensive collection of utility functions for data processing, file operations,
image handling, and common programming tasks. This library is designed to be
standalone and reusable across different projects.

Modules:
    chunk_execution: Async execution utilities with retry logic and concurrency control
    compare: Data comparison utilities for dictionaries and lists
    convert: Data conversion utilities for various formats and types
    DictDot: Dot notation access for dictionaries
    files: File and folder operation utilities
    images: Image processing and manipulation utilities
    logging: Custom logging processors and utilities for domolibrary2
    read_creds_from_dotenv: Environment credential reading utilities
    upload_data: Data upload utilities (may require external dependencies)
    xkcd_password: Password generation utilities
    exceptions: Custom exception classes for error handling

Usage:
    >>> from utils import chunk_execution, convert, DictDot
    >>> from utils.exceptions import UtilityError

    >>> # Use async utilities
    >>> await chunk_execution.run_with_retry(my_function)

    >>> # Convert data formats
    >>> datetime_obj = convert.convert_string_to_datetime("2023-01-01")

    >>> # Use dot notation for dictionaries
    >>> data = DictDot.DictDot({"user": {"name": "John"}})
    >>> print(data.user.name)  # "John"

Version: 1.0.0
Author: Domo Utils Contributors
License: MIT
"""

# Import exceptions for easy access
from . import (
    DictDot,
    chunk_execution,
    compare,
    convert,
    files,
    images,
    logging,
    read_creds_from_dotenv,
    xkcd_password,
)
from .exceptions import (
    ConcatDataframeError,
    CredentialsError,
    FileOperationError,
    ImageProcessingError,
    InvalidEmailError,
    UtilityError,
)

# Import legacy exception names from convert module for backwards compatibility


# Conditional import for upload_data (may have external dependencies)
# from . import upload_data


__all__ = [
    # Exception classes
    "UtilityError",
    "InvalidEmailError",
    "ConcatDataframeError",
    "FileOperationError",
    "ImageProcessingError",
    "CredentialsError",
    # Utility modules
    "chunk_execution",
    "compare",
    "convert",
    "DictDot",
    "files",
    "images",
    "logging",
    "read_creds_from_dotenv",
    "xkcd_password",
]
