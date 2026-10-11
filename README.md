# PlantPulse — Industrial Reliability & Maintenance Analytics

**SQL-first portfolio project | PostgreSQL · Python · Pandas · Streamlit · Plotly**

PlantPulse explores synthetic industrial equipment records to help users investigate recorded failures, downtime, maintenance expenditure, inspection condition, and open work orders. It combines a relational SQL data model with analytical queries, data-quality checks, and an interactive dashboard.

> **Data and safety note:** The bundled records are synthetic and fictional. This is a portfolio demonstration, not a validated reliability model and not a tool for operational maintenance decisions.

## What this project demonstrates
- Relational schema design, primary/foreign keys, check constraints, and indexes in PostgreSQL
- Analytical SQL with joins, CTEs, aggregates, date functions, and window functions
- Descriptive reliability analysis: event counts, downtime concentration, failure-mode patterns, maintenance spend
- Data-quality checks and documented assumptions
- Interactive dashboard design with filters, KPI cards, and Plotly charts
- Clear communication of data limitations and cautious interpretation

## Project questions
1. Which equipment has the most recorded downtime?
2. Which failure modes are most frequent, and which have the largest synthetic estimated impact?
3. How do recorded failures change month by month?
4. How does maintenance expenditure vary by maintenance type?
5. What is the latest recorded inspection condition for each equipment item?
6. Which high-priority work orders remain active?
7. Which equipment has repeated events of the same failure type?

## Repository structure
```text
industrial_reliability_analytics/
├── app/
│   └── streamlit_app.py
├── data/
│   ├── equipment.csv
│   ├── failure_events.csv
│   ├── inspections.csv
│   ├── maintenance_records.csv
│   └── work_orders.csv
├── docs/
│   ├── DATA_DICTIONARY.md
│   ├── INSIGHTS_TEMPLATE.md
│   └── PROJECT_OVERVIEW.md
├── sql/
│   ├── 01_schema.sql
│   ├── 02_seed_data.sql
│   ├── 03_analysis_queries.sql
│   └── 04_data_quality_checks.sql
├── tests/
│   └── test_data_quality.py
├── requirements.txt
└── README.md
```

## Data inventory
- 30 equipment records
- 180 failure events
- 220 maintenance records
- 150 inspection records
- 120 work orders

The data is generated for demonstration and should not be represented as real company or plant data.

## Run the SQL project
1. Install PostgreSQL and create a database named `reliability_analytics`.
2. Execute the SQL files in this order using pgAdmin or `psql`:
   1. `sql/01_schema.sql`
   2. `sql/02_seed_data.sql`
   3. `sql/03_analysis_queries.sql`
   4. `sql/04_data_quality_checks.sql`

Using `psql`:
```bash
createdb reliability_analytics
psql -d reliability_analytics -f sql/01_schema.sql
psql -d reliability_analytics -f sql/02_seed_data.sql
psql -d reliability_analytics -f sql/03_analysis_queries.sql
psql -d reliability_analytics -f sql/04_data_quality_checks.sql
```

## Run the interactive dashboard
The dashboard reads the bundled CSV snapshots so it can run independently of a live database.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Run data checks
```bash
pip install pandas pytest
pytest -q
```

## Suggested dashboard walkthrough
- Filter by plant area and equipment criticality.
- Compare monthly failure event counts.
- Inspect the failure types with the most recorded events.
- Review the top equipment by recorded downtime.
- Compare maintenance spend by activity type.
- Inspect the latest available condition rating and high-priority active work orders.

## Analytical cautions
- **Failure count is not a failure rate** unless exposure or operating hours are known.
- **MTBF and MTTR are not reported as validated metrics** because complete exposure and linked repair-event data are not supplied.
- **Estimated impact cost and maintenance cost are synthetic** and are not measured financial losses.
- **Criticality is a categorical input**, not a model-generated risk score.
- A high recorded downtime total is a reason to investigate the records, not proof of root cause or a maintenance prescription.

## Resume wording (after you have run and reviewed it)
**PlantPulse — Industrial Reliability & Maintenance Analytics | PostgreSQL, SQL, Python, Pandas, Streamlit**
- Designed a relational PostgreSQL schema for equipment, failure events, inspections, maintenance records, and work orders, using keys, constraints, and indexes.
- Developed SQL analyses with joins, CTEs, aggregations, and window functions to examine failure patterns, recorded downtime, maintenance spending, and work-order status.
- Built an interactive dashboard to explore failure trends, equipment downtime, inspection conditions, and maintenance priorities.

Use these bullets only after you have executed the project and can explain the queries, data model, and limitations in an interview.

## Next steps
- Run the SQL files and dashboard locally.
- Capture clear screenshots for the README and GitHub repository.
- Add a short findings section using actual query outputs; do not invent results.
- If replacing synthetic data with a public dataset, cite the source and update the schema and documentation.
