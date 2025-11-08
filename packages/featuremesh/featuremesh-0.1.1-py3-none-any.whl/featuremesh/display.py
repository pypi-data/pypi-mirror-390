"""
Display utilities for FeatureMesh query results.

This module provides functions to format and display:
- Errors and warnings from API responses
- Translation results (FeatureQL to SQL)
- Query results with DataFrames

All display functions are designed to work well in both terminal and Jupyter environments.
"""

from typing import Optional
from .results import Error, Warning, TranslateResult, QueryResult

__all__ = [
    "display_errors",
    "display_warnings",
    "display_translate_result",
    "display_query_result",
]


def display_errors(errors: list[Error]) -> None:
    """Display errors in a formatted way."""
    if not errors:
        return

    print("*** Error(s) occurred! ***")
    for error in errors:
        print(f"Error code: {error.code}")
        print(f"Error message: {error.message}")
        if error.context:
            print(f"Error context: {error.context}")
        if error.location:
            print(f"Error location: {error.location}")
        if error.stack_trace:
            print("\nStack trace:")
            for line in error.stack_trace:
                print(line)


def display_warnings(warnings: list[Warning]) -> None:
    """Display warnings in a formatted way."""
    if not warnings:
        return

    print("*** Query successfully executed with some warnings! ***")
    for warning in warnings:
        print(f"Warning code: {warning.code}")
        print(f"Warning message: {warning.message}")
        if warning.location:
            print(f"Warning location: {warning.location}")


def display_translate_result(result: TranslateResult, show_sql: bool = False) -> None:
    """Display a TranslateResult."""
    display_errors(result.errors)
    display_warnings(result.warnings)

    if show_sql and result.sql:
        print(result.sql)


def display_query_result(
    result: QueryResult,
    show_sql: bool = False,
    show_slt: bool = False,
    show_dataframe: bool = True,
) -> Optional[object]:
    """
    Display a QueryResult and return the dataframe for notebook display.

    Args:
        result: The QueryResult to display
        show_sql: Whether to print the SQL
        show_slt: Whether to print the SLT
        show_dataframe: Whether to return the dataframe for display

    Returns:
        The dataframe if show_dataframe is True, None otherwise
    """
    display_errors(result.errors)
    display_warnings(result.warnings)

    if show_sql and result.sql:
        print(result.sql)

    if show_slt and result.slt:
        print(result.slt)

    if show_dataframe:
        return result.dataframe
    
    return None
