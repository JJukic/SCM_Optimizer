# First Model Design: Capacity and Mix Optimization (OR-Tools)

## Model Goal

Build a first runnable optimization model for a mixed plant that allocates weekly production quantities across products and lines.

Primary objective:
- Maximize total contribution margin while respecting line capacities and demand limits.

## Decision Variables

For each product-line combination `(p, l)` that is technically feasible:
- `x[p, l] >= 0`: planned production quantity of product `p` on line `l`.

## Objective Function

Maximize:
- `sum(p, l) contribution_margin[p] * x[p, l]`

Interpretation:
- Favor high-margin production while still bounded by physical and demand constraints.

## Constraints

1. Demand upper bound per product:
- `sum(l) x[p, l] <= demand[p]`

2. Line capacity per week:
- `sum(p) hours_per_unit[p, l] * x[p, l] <= net_capacity[l]`
- `net_capacity[l] = available_capacity[l] - reserved_capacity_for_service_parts[l]`

3. Non-negativity:
- `x[p, l] >= 0`

## Input Data (First Prototype)

- `products`: product and family mapping
- `demand`: weekly demand per product
- `line_capacities`: available weekly line capacities
- `contribution_margins`: unit contribution margin per product
- `resource_usage`: hours per produced unit for each product-line combination
- `service_parts_reserve` (optional): line capacity reserved for service-part disruptions

## Expected Outputs

- Production recommendation DataFrame with columns such as:
  - `product_id`, `product_family`, `line_id`, `planned_qty`
  - `hours_per_unit`, `capacity_hours_used`
  - `unit_margin`, `contribution_margin`
- Solver status and objective value
- KPI summary:
  - total planned volume
  - total contribution margin
  - capacity utilization by line

## OR-Tools Choice

This first model uses `ortools.linear_solver.pywraplp` with `GLOP` by default.

Rationale:
- Lightweight and production-oriented Python API
- Fast to implement and test for linear models
- Can evolve into mixed-integer variants (e.g., lot sizing, setup decisions) later

## Implementation Scope (Current Step)

- One-week model run
- Linear continuous variables (no integer decisions yet)
- Clear input validation and deterministic test coverage
- No advanced sequencing or stochastic logic in this step
