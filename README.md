# SCM Optimizer

SCM Optimizer is a production-oriented Python project scaffold for supply chain optimization in a mixed manufacturing environment.

The target plant context includes:
- Two high-volume product families
- One unstable custom product family
- A service-parts stream that regularly disrupts weekly planning

This repository currently provides a clean technical foundation for later LP/MIP optimization modules. The business logic is intentionally minimal and modular to support iterative model development.

## Optimization Stack

- Primary optimization library: **OR-Tools**
- First model backend: `ortools.linear_solver.pywraplp` (`GLOP`)

## Repository Structure

```text
SCM_Optimizer/
├─ README.md
├─ .gitignore
├─ AGENTS.md
├─ requirements.txt
├─ pyproject.toml
├─ .env.example
├─ data/
│  ├─ raw/
│  ├─ processed/
│  └─ sample/
├─ notebooks/
├─ src/
│  └─ scm_optimizer/
│     ├─ config.py
│     ├─ data_loader.py
│     ├─ validation.py
│     ├─ models/
│     ├─ scenarios/
│     └─ reporting/
├─ tests/
└─ docs/
```

## Setup

1. Create and activate a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

3. Create local environment file:

```bash
cp .env.example .env
```

## Run Tests

```bash
pytest
```

## First Optimization Use Case

The first implementation target is a **weekly Capacity-and-Mix Optimization** model.

Why this first:
- High business impact on service level and throughput
- Repeats every planning cycle (weekly)
- Can be modeled as LP with available core data
- Creates baseline decisions before sequence-level MIP complexity

Initial scope:
- Decide product-level weekly production quantities across lines
- Respect line capacities (including optional service-parts reserve)
- Maximize total contribution margin
- Produce structured outputs and KPI reporting

Detailed design and data requirements:
- `docs/use_case_breakdown.md`
- `docs/first_model_design.md`
- `docs/data_requirements.md`

### Run First Model Locally

```bash
python3 -c "from scm_optimizer.models.capacity_mix_lp import build_synthetic_capacity_mix_inputs, solve_capacity_mix_lp; r = solve_capacity_mix_lp(build_synthetic_capacity_mix_inputs()); print(r.status, r.objective_value); print(r.production_plan[['product_id','line_id','planned_qty']])"
```

## Short Roadmap

1. Phase 1: Scaffolding and data validation
2. Phase 2: Capacity/Mix LP model foundations
3. Phase 3: Bottleneck sequencing MIP design
4. Phase 4: Service-parts re-planning logic
