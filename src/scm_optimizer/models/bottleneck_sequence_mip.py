"""Placeholder scaffolding for future bottleneck sequencing MIP logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class BottleneckSequenceInputs:
    """Input containers for bottleneck sequencing problems."""

    work_orders: pd.DataFrame
    resource_calendar: pd.DataFrame


def build_bottleneck_sequence_mip(
    inputs: BottleneckSequenceInputs,
    solver_name: str = "cbc",
) -> dict[str, Any]:
    """Return a placeholder response for future sequencing MIP implementation.

    TODO:
    - Define binary sequencing decisions between jobs.
    - Introduce setup-time and changeover constraints.
    - Add objective terms for lateness, setup cost, and stability.
    """
    return {
        "status": "placeholder_not_solved",
        "solver_name": solver_name,
        "scheduled_orders": 0,
        "message": "Bottleneck sequencing MIP not implemented yet.",
    }
