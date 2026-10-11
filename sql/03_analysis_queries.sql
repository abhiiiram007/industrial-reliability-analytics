-- Industrial Reliability Analytics: analyst query portfolio
-- PostgreSQL syntax. Run after 01_schema.sql and 02_seed_data.sql.

-- 1. Overall operational KPIs
SELECT
    (SELECT COUNT(*) FROM equipment) AS equipment_count,
    (SELECT COUNT(*) FROM failure_events) AS recorded_failures,
    (SELECT ROUND(SUM(downtime_hours), 2) FROM failure_events) AS total_downtime_hours,
    (SELECT ROUND(SUM(maintenance_cost), 2) FROM maintenance_records) AS total_maintenance_cost;

-- 2. Equipment with the highest downtime
SELECT e.equipment_id, e.equipment_name, e.equipment_type, e.criticality,
       COUNT(f.failure_id) AS failure_count,
       ROUND(COALESCE(SUM(f.downtime_hours), 0), 2) AS total_downtime_hours
FROM equipment e
LEFT JOIN failure_events f ON f.equipment_id = e.equipment_id
GROUP BY e.equipment_id, e.equipment_name, e.equipment_type, e.criticality
ORDER BY total_downtime_hours DESC;

-- 3. Failure pattern by type and severity
SELECT failure_type, severity, COUNT(*) AS event_count,
       ROUND(AVG(downtime_hours), 2) AS avg_downtime_hours,
       ROUND(SUM(estimated_impact_cost), 2) AS estimated_impact_cost
FROM failure_events
GROUP BY failure_type, severity
ORDER BY event_count DESC, estimated_impact_cost DESC;

-- 4. Monthly failures and downtime
SELECT DATE_TRUNC('month', failure_timestamp)::date AS failure_month,
       COUNT(*) AS failure_count,
       ROUND(SUM(downtime_hours), 2) AS downtime_hours
FROM failure_events
GROUP BY 1
ORDER BY 1;

-- 5. Maintenance spend by type
SELECT maintenance_type, COUNT(*) AS maintenance_jobs,
       ROUND(SUM(maintenance_cost), 2) AS total_cost,
       ROUND(AVG(duration_hours), 2) AS avg_duration_hours
FROM maintenance_records
GROUP BY maintenance_type
ORDER BY total_cost DESC;

-- 6. Latest inspection per equipment using ROW_NUMBER
WITH ranked_inspections AS (
    SELECT i.*,
           ROW_NUMBER() OVER (
               PARTITION BY equipment_id
               ORDER BY inspection_date DESC, inspection_id DESC
           ) AS rn
    FROM inspections i
)
SELECT e.equipment_id, e.equipment_name, e.criticality,
       ri.inspection_date, ri.condition_rating, ri.finding
FROM equipment e
LEFT JOIN ranked_inspections ri
  ON ri.equipment_id = e.equipment_id AND ri.rn = 1
ORDER BY CASE ri.condition_rating
           WHEN 'Critical' THEN 1 WHEN 'Poor' THEN 2
           WHEN 'Monitor' THEN 3 WHEN 'Good' THEN 4 ELSE 5 END,
         e.criticality DESC;

-- 7. Open high-priority work orders
SELECT w.work_order_id, e.equipment_name, e.plant_area,
       w.priority, w.status, w.created_date, w.description
FROM work_orders w
JOIN equipment e ON e.equipment_id = w.equipment_id
WHERE w.status IN ('Open','In Progress','On Hold')
  AND w.priority IN ('High','Urgent')
ORDER BY CASE w.priority WHEN 'Urgent' THEN 1 ELSE 2 END, w.created_date;

-- 8. Combined equipment scorecard
WITH failures AS (
    SELECT equipment_id, COUNT(*) AS failure_count,
           SUM(downtime_hours) AS downtime_hours,
           SUM(estimated_impact_cost) AS impact_cost
    FROM failure_events GROUP BY equipment_id
),
maintenance AS (
    SELECT equipment_id, COUNT(*) AS maintenance_count,
           SUM(maintenance_cost) AS maintenance_cost
    FROM maintenance_records GROUP BY equipment_id
),
latest_condition AS (
    SELECT equipment_id, condition_rating
    FROM (
        SELECT equipment_id, condition_rating,
               ROW_NUMBER() OVER (PARTITION BY equipment_id
                                  ORDER BY inspection_date DESC, inspection_id DESC) AS rn
        FROM inspections
    ) x WHERE rn = 1
)
SELECT e.equipment_id, e.equipment_name, e.equipment_type, e.criticality,
       COALESCE(f.failure_count,0) AS failure_count,
       ROUND(COALESCE(f.downtime_hours,0),2) AS downtime_hours,
       ROUND(COALESCE(f.impact_cost,0),2) AS estimated_failure_impact,
       COALESCE(m.maintenance_count,0) AS maintenance_count,
       ROUND(COALESCE(m.maintenance_cost,0),2) AS maintenance_cost,
       lc.condition_rating
FROM equipment e
LEFT JOIN failures f ON f.equipment_id=e.equipment_id
LEFT JOIN maintenance m ON m.equipment_id=e.equipment_id
LEFT JOIN latest_condition lc ON lc.equipment_id=e.equipment_id
ORDER BY CASE e.criticality WHEN 'Critical' THEN 1 WHEN 'High' THEN 2
                            WHEN 'Medium' THEN 3 ELSE 4 END,
         COALESCE(f.downtime_hours,0) DESC;

-- 9. Repeat failure equipment (2+ occurrences of same failure type)
SELECT equipment_id, failure_type, COUNT(*) AS repeat_events,
       ROUND(SUM(downtime_hours),2) AS total_downtime
FROM failure_events
GROUP BY equipment_id, failure_type
HAVING COUNT(*) >= 2
ORDER BY repeat_events DESC, total_downtime DESC;

-- 10. Work order closure performance (only closed orders)
SELECT priority, COUNT(*) AS closed_orders,
       ROUND(AVG(closed_date - created_date), 2) AS avg_days_to_close
FROM work_orders
WHERE status='Closed' AND closed_date IS NOT NULL
GROUP BY priority
ORDER BY avg_days_to_close DESC;

-- 11. Equipment without a recorded failure
SELECT e.equipment_id, e.equipment_name, e.equipment_type
FROM equipment e
LEFT JOIN failure_events f ON f.equipment_id=e.equipment_id
WHERE f.failure_id IS NULL
ORDER BY e.equipment_name;

-- 12. Create a reusable view for equipment reliability reporting
CREATE OR REPLACE VIEW equipment_reliability_summary AS
SELECT e.equipment_id, e.equipment_name, e.equipment_type, e.plant_area, e.criticality,
       COUNT(f.failure_id) AS failure_count,
       ROUND(COALESCE(SUM(f.downtime_hours),0),2) AS total_downtime_hours,
       ROUND(COALESCE(SUM(f.estimated_impact_cost),0),2) AS estimated_failure_impact
FROM equipment e
LEFT JOIN failure_events f ON f.equipment_id=e.equipment_id
GROUP BY e.equipment_id, e.equipment_name, e.equipment_type, e.plant_area, e.criticality;

SELECT * FROM equipment_reliability_summary
ORDER BY total_downtime_hours DESC;
