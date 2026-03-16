"""Reusable data loading helpers for CSV-based SCM datasets."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scm_optimizer.config import Settings, get_settings


def resolve_csv_path(file_name: str, base_dir: Path) -> Path:
    """Resolve a CSV file path and validate that it exists."""
    file_path = base_dir / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    return file_path


def load_csv(file_name: str, base_dir: Path) -> pd.DataFrame:
    """Load a CSV file from the given directory into a DataFrame."""
    file_path = resolve_csv_path(file_name=file_name, base_dir=base_dir)
    return pd.read_csv(file_path)


def load_sample_csv(file_name: str, settings: Settings | None = None) -> pd.DataFrame:
    """Load a CSV file from the configured sample data directory."""
    active_settings = settings or get_settings()
    return load_csv(file_name=file_name, base_dir=active_settings.data_dirs.sample)


def list_sample_csv_files(settings: Settings | None = None) -> list[Path]:
    """List available CSV files in the configured sample directory."""
    active_settings = settings or get_settings()
    sample_dir = active_settings.data_dirs.sample

    if not sample_dir.exists():
        return []

    return sorted(path for path in sample_dir.iterdir() if path.is_file() and path.suffix == ".csv")
