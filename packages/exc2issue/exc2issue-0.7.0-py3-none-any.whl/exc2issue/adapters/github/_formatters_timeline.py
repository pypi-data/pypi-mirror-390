"""Timeline and error detail formatting functions.

This module contains functions for generating chronological error timelines
and detailed error information sections in consolidated issues.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from exc2issue.core.error_collection import ErrorCollection, ErrorEntry


def add_error_timeline(body_parts: list[str], error_collection: "ErrorCollection") -> None:
    """Add chronological error timeline section.

    Args:
        body_parts: List to append timeline sections to
        error_collection: Collection containing errors to format
    """
    body_parts.extend(["## Issue Timeline", ""])

    chronological_errors = error_collection.get_chronological_errors()
    for i, error_entry in enumerate(chronological_errors, 1):
        timestamp = error_entry.timestamp.strftime("%H:%M:%S.%f")[
            :-3
        ]  # Format to milliseconds
        body_parts.extend(
            [f"### {i}. {error_entry.error_record.error_type} ({timestamp})", ""]
        )

        if error_entry.error_type == "exception":
            add_exception_details(body_parts, error_entry)
        elif error_entry.error_type == "log":
            add_log_details(body_parts, error_entry)

        body_parts.append("")


def add_exception_details(body_parts: list[str], error_entry: "ErrorEntry") -> None:
    """Add exception error details to body.

    Args:
        body_parts: List to append exception details to
        error_entry: Error entry containing exception information
    """
    body_parts.extend(
        [
            f"- **Type:** {error_entry.error_record.error_type}",
            f"- **Message:** {error_entry.error_record.error_message}",
        ]
    )

    if error_entry.error_record.traceback:
        body_parts.extend(
            [
                "- **Stack Trace:**",
                "```",
                error_entry.error_record.traceback,
                "```",
            ]
        )


def add_log_details(body_parts: list[str], error_entry: "ErrorEntry") -> None:
    """Add log error details to body.

    Args:
        body_parts: List to append log details to
        error_entry: Error entry containing log information
    """
    logger_name = error_entry.source_info.get("logger_name", "unknown")
    log_level = error_entry.source_info.get("log_level", "ERROR")

    body_parts.extend(
        [
            f"- **Type:** Log {log_level}",
            f"- **Message:** {error_entry.error_record.error_message}",
            f"- **Logger:** {logger_name}",
        ]
    )

    # Add module and line info if available
    module = error_entry.source_info.get("module")
    line_number = error_entry.source_info.get("line_number")
    if module and line_number:
        body_parts.append(f"- **Location:** {module}:{line_number}")
