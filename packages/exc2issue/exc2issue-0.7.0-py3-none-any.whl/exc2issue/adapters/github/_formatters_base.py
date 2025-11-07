"""Base conversion functions for issue formatting.

This module contains the main entry points for converting ErrorRecord and
ErrorCollection objects into GitHubIssue objects.
"""

from typing import TYPE_CHECKING

from exc2issue.core.models import ErrorRecord, GitHubIssue
from exc2issue.core.utils import generate_deterministic_title, sanitize_function_name

from ._formatters_common import (
    add_error_details_section,
    add_footer,
    add_traceback_section,
)
from ._formatters_single import (
    generate_single_error_body_fallback,
    generate_single_error_body_with_ai,
)
from ._formatters_summary import generate_consolidated_issue_body

if TYPE_CHECKING:
    from exc2issue.core.error_collection import ErrorCollection


def convert_error_to_issue(
    error_record: ErrorRecord,
    labels: list[str],
    assignees: list[str] | None = None,
) -> GitHubIssue:
    """Convert ErrorRecord to GitHubIssue.

    Args:
        error_record: ErrorRecord containing error details
        labels: List of labels to apply to the issue
        assignees: List of GitHub usernames to assign the issue to

    Returns:
        GitHubIssue object ready for creation
    """
    # Generate deterministic title from error information

    sanitized_function_name = sanitize_function_name(error_record.function_name)
    title = generate_deterministic_title(
        sanitized_function_name, error_record.error_type, error_record.error_message
    )

    # Truncate title if too long (GitHub has a 256 character limit)
    if len(title) > 256:
        title = title[:253] + "..."

    # Generate body with all available information
    body_parts: list[str] = []
    add_error_details_section(body_parts, error_record)

    body_parts.extend([
        "## Function Arguments",
        f"```\n{error_record.function_args}\n```",
        "",
    ])

    add_traceback_section(body_parts, error_record)
    add_footer(body_parts)

    body = "\n".join(body_parts)

    assignees_list = assignees or []
    return GitHubIssue(title=title, body=body, labels=labels, assignees=assignees_list)


def convert_error_collection_to_issue(
    error_collection: "ErrorCollection",
    labels: list[str],
    assignees: list[str] | None = None,
    gemini_description: str | None = None,
) -> GitHubIssue:
    """Convert ErrorCollection to GitHubIssue (single or consolidated).

    Args:
        error_collection: Collection of errors from a single function execution
        labels: List of labels to apply to the issue
        assignees: List of GitHub usernames to assign the issue to
        gemini_description: Optional AI-generated description from Gemini

    Returns:
        GitHubIssue object ready for creation
    """
    # Use imported sanitize_function_name

    error_count = error_collection.get_error_count()
    function_name = error_collection.function_name
    sanitized_function_name = sanitize_function_name(function_name)
    assignees_list = assignees or []

    # HYBRID APPROACH: Single error vs Multiple errors
    if error_count == 1:
        # Single error - use existing deterministic format
        return _create_single_error_issue(
            error_collection,
            sanitized_function_name,
            labels,
            assignees_list,
            gemini_description,
        )

    # Multiple errors - use consolidated format
    return _create_consolidated_error_issue(
        error_collection,
        labels,
        assignees_list,
        gemini_description,
    )


def _create_single_error_issue(
    error_collection: "ErrorCollection",
    sanitized_function_name: str,
    labels: list[str],
    assignees: list[str],
    gemini_description: str | None = None,
) -> GitHubIssue:
    """Create a single error issue using existing deterministic format.

    Args:
        error_collection: Collection with exactly one error
        sanitized_function_name: Sanitized function name
        labels: List of labels to apply
        assignees: List of assignees
        gemini_description: Optional AI-generated description

    Returns:
        GitHubIssue with deterministic title format
    """
    # Use imported generate_deterministic_title

    # Get the single error
    single_error_entry = error_collection.get_chronological_errors()[0]
    error_record = single_error_entry.error_record

    # Generate deterministic title using existing logic
    title = generate_deterministic_title(
        sanitized_function_name,
        error_record.error_type,
        error_record.error_message,
    )

    # Truncate title if too long
    if len(title) > 256:
        title = title[:253] + "..."

    # Generate body - use existing single error format or enhanced version
    if gemini_description:
        body = generate_single_error_body_with_ai(error_record, gemini_description)
    else:
        body = generate_single_error_body_fallback(error_record)

    return GitHubIssue(
        title=title,
        body=body,
        labels=labels,  # No additional consolidated tag
        assignees=assignees,
    )


def _create_consolidated_error_issue(
    error_collection: "ErrorCollection",
    labels: list[str],
    assignees: list[str],
    gemini_description: str | None = None,
) -> GitHubIssue:
    """Create a consolidated error issue for multiple errors.

    Args:
        error_collection: Collection with multiple errors
        labels: List of labels to apply
        assignees: List of assignees
        gemini_description: Optional AI-generated description

    Returns:
        GitHubIssue with consolidated format
    """
    # Generate consolidated title
    sanitized_function_name = sanitize_function_name(error_collection.function_name)
    error_count = error_collection.get_error_count()
    title = f"[CONSOLIDATED] {sanitized_function_name} - {error_count} Issues Detected"

    # Truncate title if too long
    if len(title) > 256:
        title = title[:253] + "..."

    # Generate comprehensive body with timeline
    body = generate_consolidated_issue_body(error_collection, gemini_description)

    return GitHubIssue(
        title=title,
        body=body,
        labels=labels + ["consolidated-error"],  # Add consolidated tag
        assignees=assignees,
    )
