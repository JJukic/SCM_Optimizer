"""Validation helpers for tabular inputs used in optimization modules."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


def missing_required_columns(df: pd.DataFrame, required_columns: Iterable[str]) -> set[str]:
    """Return the set of required columns that are missing in `df`."""
    required = set(required_columns)
    return required.difference(df.columns)


def validate_required_columns(df: pd.DataFrame, required_columns: Iterable[str]) -> None:
    """Validate that all required columns exist in `df`."""
    missing = missing_required_columns(df=df, required_columns=required_columns)
    if missing:
        formatted = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {formatted}")


def columns_with_missing_values(
    df: pd.DataFrame, columns: Iterable[str] | None = None
) -> dict[str, int]:
    """Return missing-value counts by column for selected columns."""
    selected_columns = list(columns) if columns is not None else list(df.columns)

    missing_counts: dict[str, int] = {}
    for column in selected_columns:
        null_count = int(df[column].isna().sum())
        if null_count > 0:
            missing_counts[column] = null_count

    return missing_counts


def validate_no_missing_values(df: pd.DataFrame, columns: Iterable[str] | None = None) -> None:
    """Validate that selected columns do not contain missing values."""
    missing_counts = columns_with_missing_values(df=df, columns=columns)
    if missing_counts:
        details = ", ".join(
            f"{column}={count}" for column, count in sorted(missing_counts.items())
        )
        raise ValueError(f"Missing values detected: {details}")


def validate_schema_assumptions(
    df: pd.DataFrame,
    numeric_columns: Iterable[str] | None = None,
    non_negative_columns: Iterable[str] | None = None,
) -> list[str]:
    """Check simple schema assumptions and return a list of issues."""
    issues: list[str] = []

    for column in numeric_columns or []:
        if not pd.api.types.is_numeric_dtype(df[column]):
            issues.append(f"Column '{column}' must be numeric.")

    for column in non_negative_columns or []:
        if (df[column] < 0).any():
            issues.append(f"Column '{column}' contains negative values.")

    return issues
