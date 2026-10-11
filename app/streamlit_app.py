from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

st.set_page_config(
    page_title="PlantPulse | Reliability Analytics",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container {padding-top: 1.6rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background: #f6f8fb; border: 1px solid #e4e9f0; padding: 14px 16px; border-radius: 12px;}
div[data-testid="stMetricLabel"] p {font-size: .9rem;}
.small-note {color: #64748b; font-size: .88rem;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    equipment = pd.read_csv(DATA / "equipment.csv", parse_dates=["commissioned_date"])
    failures = pd.read_csv(DATA / "failure_events.csv", parse_dates=["failure_timestamp"])
    maintenance = pd.read_csv(DATA / "maintenance_records.csv", parse_dates=["maintenance_date"])
    inspections = pd.read_csv(DATA / "inspections.csv", parse_dates=["inspection_date"])
    work_orders = pd.read_csv(DATA / "work_orders.csv", parse_dates=["created_date", "closed_date"])
    return equipment, failures, maintenance, inspections, work_orders

equipment, failures, maintenance, inspections, work_orders = load_data()

st.title("🏭 PlantPulse")
st.subheader("Industrial Reliability & Maintenance Analytics")
st.markdown("A SQL-first analytics portfolio project for exploring equipment failures, downtime, maintenance spend, inspection condition, and work-order backlog.")
st.caption("Portfolio demo • Synthetic sample data • Not intended for operational decisions")

with st.sidebar:
    st.header("Explore the plant")
    areas = ["All"] + sorted(equipment["plant_area"].dropna().unique().tolist())
    selected_area = st.selectbox("Plant area", areas)
    criticalities = ["All"] + ["Low", "Medium", "High", "Critical"]
    selected_criticality = st.selectbox("Equipment criticality", criticalities)
    start = failures["failure_timestamp"].min().date()
    end = failures["failure_timestamp"].max().date()
    date_range = st.date_input("Failure date range", value=(start, end), min_value=start, max_value=end)
    st.divider()
    st.caption("Data source: generated synthetic records bundled with this repository.")

filtered_equipment = equipment.copy()
if selected_area != "All":
    filtered_equipment = filtered_equipment[filtered_equipment["plant_area"] == selected_area]
if selected_criticality != "All":
    filtered_equipment = filtered_equipment[filtered_equipment["criticality"] == selected_criticality]
allowed_ids = set(filtered_equipment["equipment_id"])

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
else:
    start_date, end_date = pd.Timestamp(start), pd.Timestamp(end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

f = failures[(failures["equipment_id"].isin(allowed_ids)) & failures["failure_timestamp"].between(start_date, end_date)]
m = maintenance[maintenance["equipment_id"].isin(allowed_ids) & maintenance["maintenance_date"].between(start_date.normalize(), end_date.normalize())]
i = inspections[inspections["equipment_id"].isin(allowed_ids) & inspections["inspection_date"].between(start_date.normalize(), end_date.normalize())]
w = work_orders[work_orders["equipment_id"].isin(allowed_ids)]

failure_count = len(f)
downtime = float(f["downtime_hours"].sum()) if not f.empty else 0
maintenance_cost = float(m["maintenance_cost"].sum()) if not m.empty else 0
open_wo = int(w["status"].isin(["Open", "In Progress", "On Hold"]).sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Equipment in scope", f"{len(filtered_equipment):,}")
c2.metric("Recorded failures", f"{failure_count:,}")
c3.metric("Downtime hours", f"{downtime:,.1f}")
c4.metric("Maintenance spend", f"₹{maintenance_cost:,.0f}")
st.caption(f"Open / active / on-hold work orders in scope: **{open_wo:,}**")

st.divider()
left, right = st.columns([1.15, 1])
with left:
    st.markdown("### Failure trend")
    if f.empty:
        st.info("No failure events match these filters.")
    else:
        trend = f.assign(month=f["failure_timestamp"].dt.to_period("M").dt.to_timestamp()).groupby("month", as_index=False).agg(
            failures=("failure_id", "count"), downtime_hours=("downtime_hours", "sum")
        )
        fig = px.line(trend, x="month", y="failures", markers=True, title="Monthly recorded failure events",
                      labels={"month":"Month", "failures":"Failure events"})
        fig.update_layout(margin=dict(l=10,r=10,t=45,b=10), height=330)
        st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("### Failure modes")
    if f.empty:
        st.info("No failure events match these filters.")
    else:
        modes = f.groupby("failure_type", as_index=False).agg(events=("failure_id","count"), downtime_hours=("downtime_hours","sum")).sort_values("events", ascending=False)
        fig = px.bar(modes, x="events", y="failure_type", orientation="h", title="Recorded events by failure type",
                     labels={"events":"Events","failure_type":"Failure type"})
        fig.update_layout(margin=dict(l=10,r=10,t=45,b=10), height=330, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(fig, use_container_width=True)

st.divider()
left, right = st.columns(2)
with left:
    st.markdown("### Equipment downtime ranking")
    if f.empty:
        st.info("No failure events match these filters.")
    else:
        ranking = f.groupby("equipment_id", as_index=False).agg(
            failure_count=("failure_id","count"), downtime_hours=("downtime_hours","sum"),
            estimated_impact_cost=("estimated_impact_cost","sum")
        ).merge(filtered_equipment[["equipment_id","equipment_name","criticality","plant_area"]], on="equipment_id", how="left")
        ranking = ranking.sort_values("downtime_hours", ascending=False).head(10)
        fig = px.bar(ranking, x="downtime_hours", y="equipment_name", orientation="h", color="criticality",
                     hover_data=["failure_count","estimated_impact_cost","plant_area"],
                     labels={"downtime_hours":"Downtime (hours)","equipment_name":"Equipment","criticality":"Criticality"},
                     title="Top 10 equipment by recorded downtime")
        fig.update_layout(margin=dict(l=10,r=10,t=45,b=10), height=380, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("### Maintenance spend by type")
    if m.empty:
        st.info("No maintenance records match these filters.")
    else:
        spend = m.groupby("maintenance_type", as_index=False).agg(
            jobs=("maintenance_id","count"), maintenance_cost=("maintenance_cost","sum")
        ).sort_values("maintenance_cost", ascending=False)
        fig = px.pie(spend, names="maintenance_type", values="maintenance_cost", hole=.52,
                     title="Share of recorded maintenance spend")
        fig.update_layout(margin=dict(l=10,r=10,t=45,b=10), height=380)
        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown("### Latest inspection conditions")
if i.empty:
    st.info("No inspection records match these filters.")
else:
    latest = i.sort_values(["inspection_date","inspection_id"]).groupby("equipment_id", as_index=False).tail(1)
    latest = latest.merge(filtered_equipment[["equipment_id","equipment_name","equipment_type","criticality","plant_area"]], on="equipment_id", how="left")
    order = {"Critical":0,"Poor":1,"Monitor":2,"Good":3}
    latest["_order"] = latest["condition_rating"].map(order).fillna(4)
    latest = latest.sort_values(["_order","inspection_date"], ascending=[True,False])
    st.dataframe(latest[["equipment_id","equipment_name","equipment_type","plant_area","criticality","inspection_date","condition_rating","finding"]],
                 use_container_width=True, hide_index=True)

st.markdown("### High-priority open work orders")
active = w[(w["status"].isin(["Open","In Progress","On Hold"])) & (w["priority"].isin(["High","Urgent"]))].merge(
    filtered_equipment[["equipment_id","equipment_name","plant_area","criticality"]], on="equipment_id", how="left"
)
if active.empty:
    st.success("No high-priority active work orders match the current scope.")
else:
    st.dataframe(active[["work_order_id","equipment_name","plant_area","criticality","priority","status","created_date","description"]]
                 .sort_values(["priority","created_date"], ascending=[True,True]), use_container_width=True, hide_index=True)

st.download_button("Download filtered failure events (CSV)", data=f.to_csv(index=False).encode("utf-8"),
                   file_name="filtered_failure_events.csv", mime="text/csv")

with st.expander("How to interpret this dashboard"):
    st.markdown("""
    - Counts and totals describe only the synthetic records included in this demo.
    - Recorded downtime is not equivalent to equipment availability unless operating-time exposure is known.
    - The estimated impact cost is illustrative synthetic data, not measured financial loss.
    - The dashboard supports descriptive analysis; it is not a validated risk model or maintenance instruction.
    """)
