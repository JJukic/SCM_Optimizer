"""KPI helpers for production planning and optimization outputs."""

from __future__ import annotations

from typing import Any

import pandas as pd


def calculate_total_planned_volume(
    production_plan: pd.DataFrame,
    quantity_col: str = "planned_qty",
) -> float:
    """Calculate total planned production volume."""
    if quantity_col not in production_plan.columns:
        return 0.0
    return float(production_plan[quantity_col].sum())


def calculate_total_contribution_margin(
    production_plan: pd.DataFrame,
    margin_col: str = "contribution_margin",
) -> float:
    """Calculate total contribution margin from the optimization plan."""
    if margin_col not in production_plan.columns:
        return 0.0
    return float(production_plan[margin_col].sum())


def summarize_capacity_utilization(
    production_plan: pd.DataFrame,
    line_capacities: pd.DataFrame,
    line_col: str = "line_id",
    used_hours_col: str = "capacity_hours_used",
    capacity_col: str = "available_capacity",
) -> pd.DataFrame:
    """Return line-level capacity utilization summary."""
    if production_plan.empty:
        used = pd.DataFrame(columns=[line_col, "used_capacity"])
    else:
        used = (
            production_plan.groupby(line_col, as_index=False)[used_hours_col]
            .sum()
            .rename(columns={used_hours_col: "used_capacity"})
        )

    capacity = line_capacities[[line_col, capacity_col]].copy()
    summary = capacity.merge(used, on=line_col, how="left")
    summary["used_capacity"] = summary["used_capacity"].fillna(0.0)
    summary["unused_capacity"] = summary[capacity_col] - summary["used_capacity"]
    summary["utilization"] = summary.apply(
        lambda row: 0.0
        if float(row[capacity_col]) <= 0
        else float(row["used_capacity"]) / float(row[capacity_col]),
        axis=1,
    )

    return summary.sort_values(line_col, ignore_index=True)


def calculate_throughput(plan: pd.DataFrame, quantity_col: str = "planned_qty") -> float:
    """Backward-compatible alias for total planned volume."""
    return calculate_total_planned_volume(plan, quantity_col=quantity_col)


def calculate_utilization(total_load: float, total_capacity: float) -> float:
    """Calculate utilization ratio in [0, 1] for scalar totals."""
    if total_capacity <= 0:
        return 0.0
    utilization = total_load / total_capacity
    return float(max(0.0, min(utilization, 1.0)))


def summarize_lateness(
    orders: pd.DataFrame,
    lateness_col: str = "lateness_days",
) -> dict[str, Any]:
    """Return a basic lateness summary for reporting placeholders."""
    if lateness_col not in orders.columns:
        return {"late_orders": 0, "avg_lateness_days": 0.0}

    late_mask = orders[lateness_col] > 0
    late_orders = int(late_mask.sum())
    avg_lateness = float(orders.loc[late_mask, lateness_col].mean()) if late_orders else 0.0

    return {
        "late_orders": late_orders,
        "avg_lateness_days": avg_lateness,
    }
