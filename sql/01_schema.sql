-- Industrial Reliability Analytics | PostgreSQL
-- All records in this project are synthetic and intended for learning/demo use.

DROP TABLE IF EXISTS work_orders CASCADE;
DROP TABLE IF EXISTS inspections CASCADE;
DROP TABLE IF EXISTS maintenance_records CASCADE;
DROP TABLE IF EXISTS failure_events CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;

CREATE TABLE equipment (
    equipment_id VARCHAR(10) PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    equipment_type VARCHAR(60) NOT NULL,
    plant_area VARCHAR(60) NOT NULL,
    criticality VARCHAR(20) NOT NULL CHECK (criticality IN ('Low','Medium','High','Critical')),
    commissioned_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL
);

CREATE TABLE failure_events (
    failure_id INTEGER PRIMARY KEY,
    equipment_id VARCHAR(10) NOT NULL REFERENCES equipment(equipment_id),
    failure_timestamp TIMESTAMP NOT NULL,
    failure_type VARCHAR(60) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Low','Medium','High','Critical')),
    downtime_hours NUMERIC(8,2) NOT NULL CHECK (downtime_hours >= 0),
    estimated_impact_cost NUMERIC(12,2) NOT NULL CHECK (estimated_impact_cost >= 0),
    failure_description TEXT
);

CREATE TABLE maintenance_records (
    maintenance_id INTEGER PRIMARY KEY,
    equipment_id VARCHAR(10) NOT NULL REFERENCES equipment(equipment_id),
    maintenance_date DATE NOT NULL,
    maintenance_type VARCHAR(30) NOT NULL,
    duration_hours NUMERIC(8,2) NOT NULL CHECK (duration_hours >= 0),
    maintenance_cost NUMERIC(12,2) NOT NULL CHECK (maintenance_cost >= 0),
    technician_team VARCHAR(30),
    notes TEXT
);

CREATE TABLE inspections (
    inspection_id INTEGER PRIMARY KEY,
    equipment_id VARCHAR(10) NOT NULL REFERENCES equipment(equipment_id),
    inspection_date DATE NOT NULL,
    condition_rating VARCHAR(20) NOT NULL CHECK (condition_rating IN ('Good','Monitor','Poor','Critical')),
    finding TEXT
);

CREATE TABLE work_orders (
    work_order_id INTEGER PRIMARY KEY,
    equipment_id VARCHAR(10) NOT NULL REFERENCES equipment(equipment_id),
    created_date DATE NOT NULL,
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('Low','Medium','High','Urgent')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('Open','In Progress','Closed','On Hold')),
    closed_date DATE,
    description TEXT,
    CHECK (closed_date IS NULL OR closed_date >= created_date)
);

CREATE INDEX idx_failure_equipment_time ON failure_events(equipment_id, failure_timestamp);
CREATE INDEX idx_failure_type_severity ON failure_events(failure_type, severity);
CREATE INDEX idx_maintenance_equipment_date ON maintenance_records(equipment_id, maintenance_date);
CREATE INDEX idx_inspections_equipment_date ON inspections(equipment_id, inspection_date);
CREATE INDEX idx_work_orders_status_priority ON work_orders(status, priority);
