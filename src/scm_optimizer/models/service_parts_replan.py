"""Placeholder scaffolding for service-parts re-planning logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ServicePartsReplanInputs:
    """Input containers for service-parts re-planning runs."""

    base_plan: pd.DataFrame
    service_part_demand: pd.DataFrame
    current_wip: pd.DataFrame | None = None


def run_service_parts_replan(
    inputs: ServicePartsReplanInputs,
    frozen_horizon_days: int = 3,
) -> dict[str, Any]:
    """Return placeholder output for service-parts re-planning.

    TODO:
    - Define priority rules for service parts in constrained windows.
    - Quantify plan disturbance versus service-level recovery.
    - Add re-plan guardrails for frozen horizons and shop-floor stability.
    """
    return {
        "status": "placeholder_not_solved",
        "frozen_horizon_days": frozen_horizon_days,
        "updated_orders": 0,
        "message": "Service-parts re-planning logic not implemented yet.",
    }
