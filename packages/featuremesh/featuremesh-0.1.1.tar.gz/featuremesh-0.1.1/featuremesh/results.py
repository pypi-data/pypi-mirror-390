"""
Result data classes for FeatureMesh operations.

This module defines dataclasses to represent:
- Error: API or execution errors with context and stack traces
- Warning: Non-blocking warnings from API responses
- TranslateResult: Results from FeatureQL-to-SQL translation
- QueryResult: Complete results from query execution including DataFrames

All result classes include helpful string representations and success/failure properties.
"""

from dataclasses import dataclass, field
from typing import Optional
import pandas as pd

__all__ = ["Error", "Warning", "TranslateResult", "QueryResult"]


@dataclass
class Error:
    """Represents an error from the FeatureMesh API."""

    code: str
    message: str
    context: Optional[str] = None
    location: Optional[str] = None
    stack_trace: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, error_dict: dict) -> "Error":
        """Create an Error from API response dictionary."""
        extensions = error_dict.get("extensions", {})
        return cls(
            code=error_dict.get("code", "UNKNOWN"),
            message=error_dict.get("message", ""),
            context=extensions.get("context"),
            location=error_dict.get("location"),
            stack_trace=extensions.get("stack_trace", []),
        )

    def __str__(self) -> str:
        """Format error for display."""
        parts = [f"[{self.code}] {self.message}"]
        if self.context:
            parts.append(f"  Context: {self.context}")
        if self.location:
            parts.append(f"  Location: {self.location}")
        if self.stack_trace:
            parts.append(f"  Stack trace: {len(self.stack_trace)} lines")
        return "\n".join(parts)


@dataclass
class Warning:
    """Represents a warning from the FeatureMesh API."""

    code: str
    message: str
    location: Optional[str] = None

    @classmethod
    def from_dict(cls, warning_dict: dict) -> "Warning":
        """Create a Warning from API response dictionary."""
        return cls(
            code=warning_dict.get("code", "UNKNOWN"),
            message=warning_dict.get("message", ""),
            location=warning_dict.get("location"),
        )

    def __str__(self) -> str:
        """Format warning for display."""
        parts = [f"[{self.code}] {self.message}"]
        if self.location:
            parts.append(f"  Location: {self.location}")
        return "\n".join(parts)


@dataclass
class TranslateResult:
    """Result of a translate() operation."""

    featureql: str
    sql: Optional[str] = None
    warnings: list[Warning] = field(default_factory=list)
    errors: list[Error] = field(default_factory=list)
    full_response: Optional[dict] = None
    backend: Optional[str] = None
    debug_mode: bool = False
    debug_logs: Optional[dict] = None
    client_type: str = "OfflineClient"

    @property
    def success(self) -> bool:
        """Returns True if translation succeeded without errors."""
        return len(self.errors) == 0 and self.sql is not None

    def __str__(self) -> str:
        """Format result for display."""
        lines = [
            "=" * 60,
            "TranslateResult",
            "=" * 60,
        ]

        # Status
        status = "✓ SUCCESS" if self.success else "✗ FAILED"
        lines.append(f"Status: {status}")
        lines.append(f"Backend: {self.backend}")
        lines.append(f"Client: {self.client_type}")

        # Errors
        if self.errors:
            lines.append(f"\nErrors ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                lines.append(f"\n  {i}. {error}")

        # Warnings
        if self.warnings:
            lines.append(f"\nWarnings ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                lines.append(f"\n  {i}. {warning}")

        # SQL
        if self.sql:
            lines.append(f"\nSQL ({len(self.sql)} chars):")
            lines.append(
                f"  {self.sql[:100]}..." if len(self.sql) > 100 else f"  {self.sql}"
            )

        lines.append("=" * 60)
        return "\n".join(lines)


@dataclass
class QueryResult:
    """Result of a query() operation."""

    featureql: str
    sql: Optional[str] = None
    dataframe: Optional[pd.DataFrame] = None
    slt: Optional[str] = None
    warnings: list[Warning] = field(default_factory=list)
    errors: list[Error] = field(default_factory=list)
    backend: Optional[str] = None
    debug_mode: bool = False
    debug_logs: Optional[dict] = None
    client_type: str = "OfflineClient"

    @property
    def success(self) -> bool:
        """Returns True if query succeeded without errors."""
        return len(self.errors) == 0 and self.dataframe is not None

    def __str__(self) -> str:
        """Format result for display."""
        lines = [
            "=" * 60,
            "QueryResult",
            "=" * 60,
        ]

        # Status
        status = "✓ SUCCESS" if self.success else "✗ FAILED"
        lines.append(f"Status: {status}")
        lines.append(f"Backend: {self.backend}")
        lines.append(f"Client: {self.client_type}")

        # Errors
        if self.errors:
            lines.append(f"\nErrors ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                lines.append(f"\n  {i}. {error}")

        # Warnings
        if self.warnings:
            lines.append(f"\nWarnings ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                lines.append(f"\n  {i}. {warning}")

        # SQL
        if self.sql:
            lines.append(f"\nSQL ({len(self.sql)} chars):")
            sql_preview = self.sql[:100] + "..." if len(self.sql) > 100 else self.sql
            lines.append(f"  {sql_preview}")

        # DataFrame
        if self.dataframe is not None:
            lines.append(f"\nDataFrame:")
            lines.append(f"  Shape: {self.dataframe.shape}")
            lines.append(f"  Columns: {list(self.dataframe.columns)}")
            if not self.dataframe.empty:
                lines.append(f"  Preview (first 3 rows):")
                for line in str(self.dataframe.head(3)).split("\n"):
                    lines.append(f"    {line}")

        # SLT
        if self.slt:
            lines.append(f"\nSLT: Available ({len(self.slt)} chars)")

        lines.append("=" * 60)
        return "\n".join(lines)
