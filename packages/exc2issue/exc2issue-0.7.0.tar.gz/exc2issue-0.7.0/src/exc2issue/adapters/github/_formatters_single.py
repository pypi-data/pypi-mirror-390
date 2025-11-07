"""Single error formatting functions.

This module contains functions for generating issue bodies for single error cases,
both with and without AI-generated descriptions.
"""

from exc2issue.core.models import ErrorRecord

from ._formatters_common import (
    add_error_details_section,
    add_footer,
    add_function_context_section,
    add_traceback_section,
    format_timestamp,
)


def generate_single_error_body_with_ai(
    error_record: ErrorRecord, gemini_description: str
) -> str:
    """Generate single error issue body with AI description.

    Args:
        error_record: The single error record
        gemini_description: AI-generated description

    Returns:
        Formatted issue body with AI analysis
    """
    body_parts: list[str] = []
    add_error_details_section(body_parts, error_record)

    body_parts.extend([
        "## AI Analysis",
        gemini_description,
        "",
    ])

    add_function_context_section(body_parts, error_record)
    add_traceback_section(body_parts, error_record)
    add_footer(body_parts)

    return "\n".join(body_parts)


def generate_single_error_body_fallback(error_record: ErrorRecord) -> str:
    """Generate single error issue body without AI (fallback).

    Args:
        error_record: The single error record

    Returns:
        Formatted issue body without AI analysis
    """
    body_parts = [
        f"# Error in function: {error_record.function_name}",
        "",
    ]

    # Add basic error info without the "Error Details" header for simpler format
    timestamp_str = format_timestamp(error_record)
    body_parts.extend([
        f"**Error Type:** {error_record.error_type}",
        f"**Error Message:** {error_record.error_message}",
        f"**Timestamp:** {timestamp_str}",
        "",
    ])

    add_function_context_section(body_parts, error_record)
    add_traceback_section(body_parts, error_record)
    add_footer(body_parts, is_ai_mode=False)

    return "\n".join(body_parts)
