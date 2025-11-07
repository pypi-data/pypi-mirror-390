"""Issue formatting utilities for the GitHub client.

This module provides a public API for converting ErrorRecord and ErrorCollection
objects into formatted GitHub issues. The implementation has been split across
multiple focused modules for better maintainability.
"""

# Re-export public API from specialized formatter modules
from ._formatters_base import (
    convert_error_collection_to_issue,
    convert_error_to_issue,
)
from ._formatters_single import (
    generate_single_error_body_fallback,
    generate_single_error_body_with_ai,
)
from ._formatters_summary import generate_consolidated_issue_body

__all__ = [
    "convert_error_to_issue",
    "convert_error_collection_to_issue",
    "generate_single_error_body_with_ai",
    "generate_single_error_body_fallback",
    "generate_consolidated_issue_body",
]
