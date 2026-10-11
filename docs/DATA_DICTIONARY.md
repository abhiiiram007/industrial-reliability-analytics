# Data Dictionary

All values are synthetic and fictional.

## equipment
- equipment_id: unique equipment key
- equipment_name: display name
- equipment_type: broad equipment category
- plant_area: fictional plant zone
- criticality: Low / Medium / High / Critical (categorical input, not calculated risk)
- commissioned_date: fictional installation date
- status: high-level status

## failure_events
- failure_id: unique failure event
- equipment_id: equipment involved
- failure_timestamp: fictional event timestamp
- failure_type: event category
- severity: categorical severity
- downtime_hours: generated duration of downtime
- estimated_impact_cost: generated illustrative cost estimate
- failure_description: fictional event note

## maintenance_records
- maintenance_id: unique maintenance record
- equipment_id: equipment serviced
- maintenance_date: service date
- maintenance_type: Preventive / Corrective / Predictive / Inspection
- duration_hours: generated maintenance duration
- maintenance_cost: generated illustrative cost
- technician_team: fictional team label
- notes: fictional maintenance note

## inspections
- inspection_id: unique inspection record
- equipment_id: inspected equipment
- inspection_date: inspection date
- condition_rating: Good / Monitor / Poor / Critical
- finding: fictional inspection observation

## work_orders
- work_order_id: unique work order
- equipment_id: equipment requiring work
- created_date: creation date
- priority: Low / Medium / High / Urgent
- status: Open / In Progress / Closed / On Hold
- closed_date: populated for closed orders
- description: fictional task summary
