-- Data quality checks. Each query should return zero rows for the corresponding issue.

-- 1. Failure events referencing missing equipment (foreign keys should prevent this).
SELECT f.*
FROM failure_events f
LEFT JOIN equipment e ON e.equipment_id = f.equipment_id
WHERE e.equipment_id IS NULL;

-- 2. Negative or null downtime.
SELECT *
FROM failure_events
WHERE downtime_hours IS NULL OR downtime_hours < 0;

-- 3. Closed work orders without a close date.
SELECT *
FROM work_orders
WHERE status = 'Closed' AND closed_date IS NULL;

-- 4. Non-closed work orders that unexpectedly have a close date.
SELECT *
FROM work_orders
WHERE status <> 'Closed' AND closed_date IS NOT NULL;

-- 5. Inspection ratings outside the allowed set.
SELECT *
FROM inspections
WHERE condition_rating NOT IN ('Good','Monitor','Poor','Critical');
