# Use Case Breakdown

## Plant Context

Wiesenhof Systems operates a mixed manufacturing site with:
- Two high-volume families (`HV_A`, `HV_B`)
- One unstable custom family (`CUST_X`)
- A service-parts stream that causes recurring weekly plan disruptions

## Decision Problems

### Continuously Optimizable (LP/MIP Candidates)

| Decision Problem | Cadence | Why It Fits Optimization | Candidate Technique |
| --- | --- | --- | --- |
| Weekly capacity-and-mix allocation across product families | Weekly (rolling) | Repeated allocation under finite capacity and competing demand | LP (with optional MILP extensions) |
| Bottleneck sequence optimization for constrained resources | Daily / shift-level | Combinatorial order sequence with setup and due-date trade-offs | MIP |
| Disruption-aware service-parts re-planning | Event-driven, often weekly | Repeated trade-off between urgent service parts and schedule stability | LP/MIP hybrid |
| Overtime and extra-shift activation under demand stress | Weekly | Cost vs. service trade-off with clear constraints | LP/MILP |

### More Rule-Based (Initial Stage)

| Decision Problem | Cadence | Why Rule-Based First |
| --- | --- | --- |
| Service-parts interruption trigger (when to re-plan) | Daily | Clear operational thresholds can be encoded as policy rules first |
| Planning freeze-window enforcement | Weekly | Governance and execution discipline are policy-driven |
| Safety capacity buffer policy by family | Weekly / monthly | Often business policy before optimization fine-tuning |

### Initially Manual / Planner-Driven

| Decision Problem | Cadence | Why Manual First |
| --- | --- | --- |
| New custom-order acceptance and due-date commitment | Event-driven | Requires cross-functional business judgment and customer negotiation |
| Exception handling for missing or late master data | Continuous | Data reliability issue, not a direct optimization problem |
| Strategic campaign shifts between high-volume families | Monthly / quarterly | Depends on commercial strategy and plant leadership priorities |

## Clear Decision Statements

1. How much should each product family produce per week, given finite resource capacity and service-part interruptions?
2. In which sequence should jobs run on bottleneck resources to reduce lateness and setup losses?
3. How should the baseline plan be adjusted when urgent service-parts demand arrives?
4. When should overtime or additional shifts be activated versus accepting backlog or lateness?

## Prioritization Matrix

Scoring scale: `1 (low) .. 5 (high)`. Higher total means earlier implementation priority.

| Decision Problem | Business Impact | Repeat Frequency | Data Availability | LP/MIP Fit | Project Feasibility | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Weekly capacity-and-mix allocation | 5 | 5 | 4 | 5 | 5 | 24 |
| Service-parts re-planning (event-driven) | 5 | 4 | 3 | 4 | 3 | 19 |
| Bottleneck sequencing optimization | 4 | 4 | 2 | 5 | 2 | 17 |
| Overtime/extra-shift activation | 3 | 4 | 4 | 4 | 4 | 19 |
| Custom-order acceptance support | 4 | 3 | 2 | 2 | 2 | 13 |

## First Recommended Use Case

Implement **Weekly Capacity-and-Mix Optimization** first.  
It has the strongest combined score and provides a stable, explainable baseline for later sequencing and disruption-replanning modules.
