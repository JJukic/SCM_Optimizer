# Initial Assumptions and Open Questions

## Initial Assumptions

- Planning horizon starts with weekly buckets.
- Demand, capacity, and routing-related inputs are provided as tabular datasets.
- High-volume families prioritize throughput stability.
- Custom-family demand is more volatile and may require flexible capacity windows.
- Service-parts demand can trigger short-term re-planning events.

## Data Assumptions

- Input files use consistent column names per domain table.
- Quantity and capacity fields are numeric and non-negative unless explicitly documented.
- Missing values in critical columns are treated as validation errors.

## Open Questions

- Which bottleneck resources are fixed versus shift-adjustable?
- What freeze windows are acceptable for shop-floor stability?
- How should service-level penalties be weighted against plan stability?
- How should OR-Tools model variants be staged (LP first, then MIP extensions)?
