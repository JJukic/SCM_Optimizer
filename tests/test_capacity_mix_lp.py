"""Tests for the OR-Tools capacity-and-mix model prototype."""

from __future__ import annotations

import pandas as pd

from scm_optimizer.models.capacity_mix_lp import (
    CapacityMixInputs,
    build_synthetic_capacity_mix_inputs,
    solve_capacity_mix_lp,
)


def test_capacity_mix_lp_solves_and_respects_core_constraints() -> None:
    """Model should solve and respect demand/capacity limits."""
    inputs = CapacityMixInputs(
        products=pd.DataFrame(
            {
                "product_id": ["P_A", "P_B", "P_C"],
                "product_family": ["HV_A", "HV_B", "CUST_X"],
            }
        ),
        demand=pd.DataFrame(
            {
                "product_id": ["P_A", "P_B", "P_C"],
                "week": [1, 1, 1],
                "demand_qty": [12.0, 8.0, 10.0],
            }
        ),
        line_capacities=pd.DataFrame(
            {
                "line_id": ["L1", "L2"],
                "week": [1, 1],
                "available_capacity": [15.0, 8.0],
            }
        ),
        contribution_margins=pd.DataFrame(
            {
                "product_id": ["P_A", "P_B", "P_C"],
                "contribution_margin": [9.0, 7.0, 11.0],
            }
        ),
        resource_usage=pd.DataFrame(
            {
                "product_id": ["P_A", "P_B", "P_C", "P_C"],
                "line_id": ["L1", "L1", "L1", "L2"],
                "hours_per_unit": [1.0, 1.2, 1.5, 1.0],
            }
        ),
        service_parts_reserve=pd.DataFrame(
            {
                "line_id": ["L1", "L2"],
                "week": [1, 1],
                "reserved_capacity": [1.0, 2.0],
            }
        ),
    )

    result = solve_capacity_mix_lp(inputs=inputs, week=1, solver_name="GLOP")

    assert result.status in {"OPTIMAL", "FEASIBLE"}
    assert isinstance(result.production_plan, pd.DataFrame)
    assert not result.production_plan.empty

    planned_by_product = (
        result.production_plan.groupby("product_id", as_index=False)["planned_qty"].sum()
    )
    demand_map = {
        row.product_id: float(row.demand_qty)
        for row in inputs.demand.itertuples(index=False)
    }
    for row in planned_by_product.itertuples(index=False):
        assert float(row.planned_qty) <= demand_map[row.product_id] + 1e-6

    used_by_line = (
        result.production_plan.groupby("line_id", as_index=False)["capacity_hours_used"].sum()
    )
    net_capacity = (
        inputs.line_capacities.merge(
            inputs.service_parts_reserve,
            on=["line_id", "week"],
            how="left",
        )
        .fillna(0.0)
        .assign(net_capacity=lambda df: df["available_capacity"] - df["reserved_capacity"])
    )
    cap_map = {
        row.line_id: float(row.net_capacity)
        for row in net_capacity.itertuples(index=False)
    }
    for row in used_by_line.itertuples(index=False):
        assert float(row.capacity_hours_used) <= cap_map[row.line_id] + 1e-6


def test_capacity_mix_lp_synthetic_helper_is_runnable() -> None:
    """Synthetic helper should return a solvable instance."""
    inputs = build_synthetic_capacity_mix_inputs()
    result = solve_capacity_mix_lp(inputs=inputs)

    assert result.status in {"OPTIMAL", "FEASIBLE"}
    assert result.objective_value is not None
    assert "kpi_summary" in result.diagnostics
