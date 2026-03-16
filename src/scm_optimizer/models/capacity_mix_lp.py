"""OR-Tools-based prototype for capacity-and-mix optimization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ortools.linear_solver import pywraplp
import pandas as pd

from scm_optimizer.reporting.kpis import (
    calculate_total_contribution_margin,
    calculate_total_planned_volume,
    summarize_capacity_utilization,
)
from scm_optimizer.validation import (
    validate_no_missing_values,
    validate_required_columns,
    validate_schema_assumptions,
)


@dataclass(frozen=True)
class CapacityMixInputs:
    """Input tables required for the capacity-and-mix optimization model."""

    products: pd.DataFrame
    demand: pd.DataFrame
    line_capacities: pd.DataFrame
    contribution_margins: pd.DataFrame
    resource_usage: pd.DataFrame
    service_parts_reserve: pd.DataFrame | None = None


@dataclass(frozen=True)
class CapacityMixResult:
    """Structured optimization result for capacity-and-mix planning."""

    status: str
    objective_value: float | None
    production_plan: pd.DataFrame
    diagnostics: dict[str, Any]


def build_synthetic_capacity_mix_inputs() -> CapacityMixInputs:
    """Build a deterministic synthetic scenario for local runs and tests."""
    products = pd.DataFrame(
        {
            "product_id": ["HV_A_1", "HV_B_1", "CUST_X_1", "SP_1"],
            "product_family": ["HV_A", "HV_B", "CUST_X", "SERVICE_PART"],
        }
    )

    demand = pd.DataFrame(
        {
            "product_id": ["HV_A_1", "HV_B_1", "CUST_X_1", "SP_1"],
            "week": [1, 1, 1, 1],
            "demand_qty": [220.0, 180.0, 70.0, 30.0],
        }
    )

    line_capacities = pd.DataFrame(
        {
            "line_id": ["LINE_A", "LINE_B"],
            "week": [1, 1],
            "available_capacity": [260.0, 240.0],
        }
    )

    contribution_margins = pd.DataFrame(
        {
            "product_id": ["HV_A_1", "HV_B_1", "CUST_X_1", "SP_1"],
            "contribution_margin": [12.0, 10.0, 20.0, 15.0],
        }
    )

    resource_usage = pd.DataFrame(
        {
            "product_id": ["HV_A_1", "HV_B_1", "CUST_X_1", "CUST_X_1", "SP_1"],
            "line_id": ["LINE_A", "LINE_A", "LINE_A", "LINE_B", "LINE_B"],
            "hours_per_unit": [1.0, 1.2, 1.8, 1.3, 0.9],
        }
    )

    service_parts_reserve = pd.DataFrame(
        {
            "line_id": ["LINE_A", "LINE_B"],
            "week": [1, 1],
            "reserved_capacity": [20.0, 15.0],
        }
    )

    return CapacityMixInputs(
        products=products,
        demand=demand,
        line_capacities=line_capacities,
        contribution_margins=contribution_margins,
        resource_usage=resource_usage,
        service_parts_reserve=service_parts_reserve,
    )


def _validate_inputs(inputs: CapacityMixInputs) -> None:
    """Validate required schema and basic data assumptions."""
    validate_required_columns(inputs.products, ["product_id", "product_family"])
    validate_required_columns(inputs.demand, ["product_id", "week", "demand_qty"])
    validate_required_columns(inputs.line_capacities, ["line_id", "week", "available_capacity"])
    validate_required_columns(inputs.contribution_margins, ["product_id", "contribution_margin"])
    validate_required_columns(inputs.resource_usage, ["product_id", "line_id", "hours_per_unit"])

    validate_no_missing_values(inputs.products, ["product_id", "product_family"])
    validate_no_missing_values(inputs.demand, ["product_id", "week", "demand_qty"])
    validate_no_missing_values(inputs.line_capacities, ["line_id", "week", "available_capacity"])
    validate_no_missing_values(inputs.contribution_margins, ["product_id", "contribution_margin"])
    validate_no_missing_values(inputs.resource_usage, ["product_id", "line_id", "hours_per_unit"])

    demand_issues = validate_schema_assumptions(
        inputs.demand,
        numeric_columns=["week", "demand_qty"],
        non_negative_columns=["demand_qty"],
    )
    capacity_issues = validate_schema_assumptions(
        inputs.line_capacities,
        numeric_columns=["week", "available_capacity"],
        non_negative_columns=["available_capacity"],
    )
    margin_issues = validate_schema_assumptions(
        inputs.contribution_margins,
        numeric_columns=["contribution_margin"],
    )
    usage_issues = validate_schema_assumptions(
        inputs.resource_usage,
        numeric_columns=["hours_per_unit"],
        non_negative_columns=["hours_per_unit"],
    )

    reserve_issues: list[str] = []
    if inputs.service_parts_reserve is not None:
        validate_required_columns(inputs.service_parts_reserve, ["line_id", "week", "reserved_capacity"])
        validate_no_missing_values(inputs.service_parts_reserve, ["line_id", "week", "reserved_capacity"])
        reserve_issues = validate_schema_assumptions(
            inputs.service_parts_reserve,
            numeric_columns=["week", "reserved_capacity"],
            non_negative_columns=["reserved_capacity"],
        )

    all_issues = demand_issues + capacity_issues + margin_issues + usage_issues + reserve_issues
    if all_issues:
        joined = " ".join(all_issues)
        raise ValueError(f"Invalid input data: {joined}")


def _prepare_week_data(
    inputs: CapacityMixInputs,
    week: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Prepare product-line planning records and net capacities for one week."""
    demand_week = (
        inputs.demand.loc[inputs.demand["week"].astype(int) == week, ["product_id", "demand_qty"]]
        .groupby("product_id", as_index=False)["demand_qty"]
        .sum()
    )
    if demand_week.empty:
        raise ValueError(f"No demand found for week {week}.")

    margin_table = (
        inputs.contribution_margins[["product_id", "contribution_margin"]]
        .groupby("product_id", as_index=False)["contribution_margin"]
        .mean()
    )
    product_table = inputs.products[["product_id", "product_family"]].drop_duplicates()
    usage_table = (
        inputs.resource_usage[["product_id", "line_id", "hours_per_unit"]]
        .groupby(["product_id", "line_id"], as_index=False)["hours_per_unit"]
        .mean()
    )

    planning_records = (
        usage_table.merge(demand_week, on="product_id", how="inner")
        .merge(margin_table, on="product_id", how="inner")
        .merge(product_table, on="product_id", how="inner")
    )

    missing_margin = set(demand_week["product_id"]) - set(margin_table["product_id"])
    if missing_margin:
        raise ValueError(f"Missing contribution margins for products: {sorted(missing_margin)}")

    missing_usage = set(demand_week["product_id"]) - set(usage_table["product_id"])
    if missing_usage:
        raise ValueError(f"Missing resource usage for products: {sorted(missing_usage)}")

    capacity_week = (
        inputs.line_capacities.loc[
            inputs.line_capacities["week"].astype(int) == week,
            ["line_id", "available_capacity"],
        ]
        .groupby("line_id", as_index=False)["available_capacity"]
        .sum()
    )

    if capacity_week.empty:
        raise ValueError(f"No line capacities found for week {week}.")

    if inputs.service_parts_reserve is not None:
        reserve_week = (
            inputs.service_parts_reserve.loc[
                inputs.service_parts_reserve["week"].astype(int) == week,
                ["line_id", "reserved_capacity"],
            ]
            .groupby("line_id", as_index=False)["reserved_capacity"]
            .sum()
        )
    else:
        reserve_week = pd.DataFrame(columns=["line_id", "reserved_capacity"])

    net_capacity = capacity_week.merge(reserve_week, on="line_id", how="left")
    net_capacity["reserved_capacity"] = net_capacity["reserved_capacity"].fillna(0.0)
    net_capacity["net_capacity"] = (
        net_capacity["available_capacity"] - net_capacity["reserved_capacity"]
    ).clip(lower=0.0)

    missing_line_cap = set(planning_records["line_id"]) - set(net_capacity["line_id"])
    if missing_line_cap:
        raise ValueError(f"Missing line capacities for lines: {sorted(missing_line_cap)}")

    return planning_records, demand_week, net_capacity


def solve_capacity_mix_lp(
    inputs: CapacityMixInputs,
    week: int = 1,
    solver_name: str = "GLOP",
) -> CapacityMixResult:
    """Solve a one-week capacity-and-mix LP using OR-Tools.

    Objective:
    - Maximize total contribution margin.

    Constraints:
    - Product demand upper bounds.
    - Line capacity limits (net of optional service-parts reserve).
    - Variable non-negativity.
    """
    _validate_inputs(inputs)
    planning_records, demand_week, net_capacity = _prepare_week_data(inputs=inputs, week=week)

    solver = pywraplp.Solver.CreateSolver(solver_name)
    if solver is None:
        raise RuntimeError(f"Failed to create OR-Tools solver '{solver_name}'.")

    decision_vars: dict[tuple[str, str], pywraplp.Variable] = {}
    for row in planning_records.itertuples(index=False):
        key = (str(row.product_id), str(row.line_id))
        decision_vars[key] = solver.NumVar(0.0, solver.infinity(), f"x_{row.product_id}_{row.line_id}")

    demand_map = {
        str(row.product_id): float(row.demand_qty)
        for row in demand_week.itertuples(index=False)
    }
    for product_id, demand_qty in demand_map.items():
        constraint = solver.Constraint(0.0, demand_qty, f"demand_{product_id}")
        for line_id in planning_records.loc[
            planning_records["product_id"] == product_id, "line_id"
        ].unique():
            constraint.SetCoefficient(decision_vars[(product_id, str(line_id))], 1.0)

    capacity_map = {
        str(row.line_id): float(row.net_capacity)
        for row in net_capacity.itertuples(index=False)
    }
    for line_id, line_capacity in capacity_map.items():
        constraint = solver.Constraint(0.0, line_capacity, f"capacity_{line_id}")
        line_rows = planning_records.loc[planning_records["line_id"] == line_id]
        for row in line_rows.itertuples(index=False):
            constraint.SetCoefficient(
                decision_vars[(str(row.product_id), str(row.line_id))],
                float(row.hours_per_unit),
            )

    objective = solver.Objective()
    for row in planning_records.itertuples(index=False):
        objective.SetCoefficient(
            decision_vars[(str(row.product_id), str(row.line_id))],
            float(row.contribution_margin),
        )
    objective.SetMaximization()

    status_code = solver.Solve()
    status_map = {
        pywraplp.Solver.OPTIMAL: "OPTIMAL",
        pywraplp.Solver.FEASIBLE: "FEASIBLE",
        pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
        pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
        pywraplp.Solver.ABNORMAL: "ABNORMAL",
        pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
    }
    status = status_map.get(status_code, f"UNKNOWN_{status_code}")

    if status_code not in {pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE}:
        return CapacityMixResult(
            status=status,
            objective_value=None,
            production_plan=pd.DataFrame(
                columns=[
                    "product_id",
                    "product_family",
                    "line_id",
                    "planned_qty",
                    "demand_qty",
                    "unit_margin",
                    "hours_per_unit",
                    "capacity_hours_used",
                    "contribution_margin",
                ]
            ),
            diagnostics={"week": week, "solver_name": solver_name, "kpi_summary": {}},
        )

    rows: list[dict[str, Any]] = []
    for row in planning_records.itertuples(index=False):
        product_id = str(row.product_id)
        line_id = str(row.line_id)
        planned_qty = float(decision_vars[(product_id, line_id)].solution_value())
        used_hours = planned_qty * float(row.hours_per_unit)
        margin_value = planned_qty * float(row.contribution_margin)

        rows.append(
            {
                "product_id": product_id,
                "product_family": str(row.product_family),
                "line_id": line_id,
                "planned_qty": planned_qty,
                "demand_qty": float(row.demand_qty),
                "unit_margin": float(row.contribution_margin),
                "hours_per_unit": float(row.hours_per_unit),
                "capacity_hours_used": used_hours,
                "contribution_margin": margin_value,
            }
        )

    production_plan = pd.DataFrame(rows).sort_values(
        ["product_id", "line_id"], ignore_index=True
    )

    capacity_summary = summarize_capacity_utilization(
        production_plan=production_plan,
        line_capacities=net_capacity[["line_id", "net_capacity"]].rename(
            columns={"net_capacity": "available_capacity"}
        ),
        capacity_col="available_capacity",
    )

    kpi_summary: dict[str, Any] = {
        "total_contribution_margin": calculate_total_contribution_margin(production_plan),
        "total_planned_volume": calculate_total_planned_volume(production_plan),
        "capacity_utilization": capacity_summary,
    }

    return CapacityMixResult(
        status=status,
        objective_value=float(objective.Value()),
        production_plan=production_plan,
        diagnostics={
            "week": week,
            "solver_name": solver_name,
            "demand_records": int(len(demand_week)),
            "decision_variables": int(len(decision_vars)),
            "kpi_summary": kpi_summary,
        },
    )
