"""Tests for validation helper functions."""

from __future__ import annotations

import pandas as pd
import pytest

from scm_optimizer.validation import (
    columns_with_missing_values,
    validate_required_columns,
    validate_schema_assumptions,
)


def test_validate_required_columns_passes_when_columns_exist() -> None:
    """Validation should pass when all required columns are present."""
    df = pd.DataFrame({"a": [1], "b": [2]})
    validate_required_columns(df=df, required_columns=["a", "b"])


def test_validate_required_columns_raises_for_missing_columns() -> None:
    """Validation should fail when required columns are missing."""
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_required_columns(df=df, required_columns=["a", "b"])


def test_columns_with_missing_values_returns_counts() -> None:
    """Missing-value counter should report only columns with null values."""
    df = pd.DataFrame({"x": [1.0, None], "y": [1, 2]})
    result = columns_with_missing_values(df=df)
    assert result == {"x": 1}


def test_validate_schema_assumptions_reports_negative_values() -> None:
    """Schema validation should flag negative values in non-negative columns."""
    df = pd.DataFrame({"qty": [10, -1]})
    issues = validate_schema_assumptions(
        df=df,
        numeric_columns=["qty"],
        non_negative_columns=["qty"],
    )
    assert "negative values" in issues[0]
