"""Central configuration objects for SCM Optimizer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


def _resolve_path(raw_value: str | None, fallback: Path) -> Path:
    """Resolve environment-provided path values against project root."""
    if not raw_value:
        return fallback

    candidate = Path(raw_value)
    if candidate.is_absolute():
        return candidate

    return PROJECT_ROOT / candidate


def _to_bool(raw_value: str | None, default: bool = False) -> bool:
    """Convert string environment values to boolean."""
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class DataDirectories:
    """Container for configured data directory paths."""

    raw: Path
    processed: Path
    sample: Path


@dataclass(frozen=True)
class RuntimeOptions:
    """Container for runtime-level default options."""

    default_horizon_weeks: int
    default_solver: str
    debug: bool


@dataclass(frozen=True)
class Settings:
    """Top-level application settings object."""

    project_root: Path
    data_dirs: DataDirectories
    runtime: RuntimeOptions


def get_settings() -> Settings:
    """Build a settings object from environment variables and defaults."""
    raw_dir = _resolve_path(os.getenv("SCM_DATA_RAW_DIR"), PROJECT_ROOT / "data" / "raw")
    processed_dir = _resolve_path(
        os.getenv("SCM_DATA_PROCESSED_DIR"), PROJECT_ROOT / "data" / "processed"
    )
    sample_dir = _resolve_path(
        os.getenv("SCM_DATA_SAMPLE_DIR"), PROJECT_ROOT / "data" / "sample"
    )

    runtime = RuntimeOptions(
        default_horizon_weeks=int(os.getenv("SCM_DEFAULT_HORIZON_WEEKS", "4")),
        default_solver=os.getenv("SCM_DEFAULT_SOLVER", "GLOP"),
        debug=_to_bool(os.getenv("SCM_DEBUG"), default=False),
    )

    return Settings(
        project_root=PROJECT_ROOT,
        data_dirs=DataDirectories(raw=raw_dir, processed=processed_dir, sample=sample_dir),
        runtime=runtime,
    )
