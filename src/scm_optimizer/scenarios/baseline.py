"""Baseline scenarios for mixed manufacturing planning experiments."""

from __future__ import annotations

from typing import Any

import pandas as pd


def build_baseline_scenario() -> dict[str, Any]:
    """Return a high-level baseline scenario dictionary."""
    return {
        "scenario_name": "baseline_mixed_manufacturing",
        "horizon_weeks": 4,
        "product_families": [
            {"id": "HV_A", "type": "high_volume"},
            {"id": "HV_B", "type": "high_volume"},
            {"id": "CUST_X", "type": "custom_unstable"},
        ],
        "service_parts": {
            "enabled": True,
            "disruption_pattern": "weekly_interruptions",
        },
        "planning_objectives": [
            "maximize contribution margin",
            "respect line capacities",
            "preserve service-parts responsiveness",
        ],
    }


def build_capacity_mix_baseline_tables() -> dict[str, pd.DataFrame]:
    """Return synthetic product/line tables for first OR-Tools model runs."""
    return {
        "products": pd.DataFrame(
            {
                "product_id": ["HV_A_1", "HV_B_1", "CUST_X_1", "SP_1"],
                "product_family": ["HV_A", "HV_B", "CUST_X", "SERVICE_PART"],
            }
        ),
        "demand": pd.DataFrame(
            {
                "product_id": ["HV_A_1", "HV_B_1", "CUST_X_1", "SP_1"],
                "week": [1, 1, 1, 1],
                "demand_qty": [220.0, 180.0, 70.0, 30.0],
            }
        ),
        "line_capacities": pd.DataFrame(
            {
                "line_id": ["LINE_A", "LINE_B"],
                "week": [1, 1],
                "available_capacity": [260.0, 240.0],
            }
        ),
        "contribution_margins": pd.DataFrame(
            {
                "product_id": ["HV_A_1", "HV_B_1", "CUST_X_1", "SP_1"],
                "contribution_margin": [12.0, 10.0, 20.0, 15.0],
            }
        ),
        "resource_usage": pd.DataFrame(
            {
                "product_id": ["HV_A_1", "HV_B_1", "CUST_X_1", "CUST_X_1", "SP_1"],
                "line_id": ["LINE_A", "LINE_A", "LINE_A", "LINE_B", "LINE_B"],
                "hours_per_unit": [1.0, 1.2, 1.8, 1.3, 0.9],
            }
        ),
        "service_parts_reserve": pd.DataFrame(
            {
                "line_id": ["LINE_A", "LINE_B"],
                "week": [1, 1],
                "reserved_capacity": [20.0, 15.0],
            }
        ),
    }
