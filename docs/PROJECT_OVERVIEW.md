# Project Overview

## Problem
Industrial maintenance teams need a consistent view of equipment failures, downtime, inspection observations, maintenance expenditure, and unresolved work orders. Scattered records make it harder to spot recurring patterns and focus review effort.

## Solution
PlantPulse is a SQL-first reliability analytics portfolio project. A normalized PostgreSQL schema stores related operational records. Analytical SQL queries produce equipment-level summaries, recurring-failure views, cost comparisons, and work-order lists. A Streamlit dashboard provides interactive descriptive exploration.

## Architecture
CSV synthetic data → PostgreSQL relational schema → SQL analysis/views → Streamlit dashboard (CSV-backed demo mode)

The dashboard currently reads the bundled CSV snapshots so it can run without a database connection. The SQL scripts demonstrate the database-first workflow separately.

## Scope and limitations
- All bundled data is synthetic.
- Estimated impact cost is illustrative only.
- No calibrated failure probability is calculated.
- No MTBF/MTTR claim is made without suitable exposure and repair-linkage data.
- Results are not intended for real plant maintenance decisions.
