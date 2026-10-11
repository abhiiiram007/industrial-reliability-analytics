from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def test_dataset_tables_exist_and_have_expected_columns():
    expected = {
        "equipment.csv": {"equipment_id", "equipment_type", "criticality", "plant_area"},
        "failure_events.csv": {"failure_id", "equipment_id", "failure_timestamp", "failure_type", "downtime_hours"},
        "maintenance_records.csv": {"maintenance_id", "equipment_id", "maintenance_type", "maintenance_cost"},
        "inspections.csv": {"inspection_id", "equipment_id", "condition_rating"},
        "work_orders.csv": {"work_order_id", "equipment_id", "priority", "status"},
    }
    for filename, columns in expected.items():
        df = pd.read_csv(DATA / filename)
        assert columns.issubset(df.columns)
        assert not df.empty

def test_primary_keys_are_unique():
    key_columns = {
        "equipment.csv": "equipment_id",
        "failure_events.csv": "failure_id",
        "maintenance_records.csv": "maintenance_id",
        "inspections.csv": "inspection_id",
        "work_orders.csv": "work_order_id",
    }
    for filename, key in key_columns.items():
        df = pd.read_csv(DATA / filename)
        assert df[key].is_unique

def test_foreign_keys_reference_known_equipment():
    equipment_ids = set(pd.read_csv(DATA / "equipment.csv")["equipment_id"])
    for filename in ["failure_events.csv", "maintenance_records.csv", "inspections.csv", "work_orders.csv"]:
        df = pd.read_csv(DATA / filename)
        assert set(df["equipment_id"]).issubset(equipment_ids)

def test_nonnegative_costs_and_durations():
    failures = pd.read_csv(DATA / "failure_events.csv")
    maintenance = pd.read_csv(DATA / "maintenance_records.csv")
    assert (failures["downtime_hours"] >= 0).all()
    assert (failures["estimated_impact_cost"] >= 0).all()
    assert (maintenance["maintenance_cost"] >= 0).all()
    assert (maintenance["duration_hours"] >= 0).all()
