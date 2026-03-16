# Data Requirements for First Use Case (OR-Tools Capacity and Mix)

## Minimal Input Tables

### 1) `products.csv`
- Purpose: product master and family mapping
- Required columns:
  - `product_id`
  - `product_family`

### 2) `demand.csv`
- Purpose: weekly demand upper bounds per product
- Required columns:
  - `product_id`
  - `week`
  - `demand_qty`

### 3) `line_capacities.csv`
- Purpose: available weekly capacity per production line
- Required columns:
  - `line_id`
  - `week`
  - `available_capacity`

### 4) `contribution_margins.csv`
- Purpose: objective coefficients by product
- Required columns:
  - `product_id`
  - `contribution_margin`

### 5) `resource_usage.csv`
- Purpose: technical feasibility and line load conversion
- Required columns:
  - `product_id`
  - `line_id`
  - `hours_per_unit`

### 6) `service_parts_reserve.csv` (optional)
- Purpose: reserve line capacity for service-parts disruptions
- Required columns:
  - `line_id`
  - `week`
  - `reserved_capacity`

## Synthetic Starter Dataset

The first OR-Tools prototype dataset lives in:
- `data/sample/capacity_mix_ortools/products.csv`
- `data/sample/capacity_mix_ortools/demand.csv`
- `data/sample/capacity_mix_ortools/line_capacities.csv`
- `data/sample/capacity_mix_ortools/contribution_margins.csv`
- `data/sample/capacity_mix_ortools/resource_usage.csv`
- `data/sample/capacity_mix_ortools/service_parts_reserve.csv`

## Early Data Quality Checks

- Required columns exist
- No missing values in key identifiers and numeric drivers
- Non-negative demand, capacity, reserve, and usage coefficients
- Full key coverage:
  - every demanded product has margins
  - every demanded product has at least one product-line usage row
  - every referenced line has capacity in the solved week
