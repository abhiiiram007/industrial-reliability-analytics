from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ------------------------------------------------------------
# PlantPulse — Industrial Reliability & Maintenance Analytics
# ------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

st.set_page_config(
    page_title="PlantPulse | Reliability Analytics",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Industrial palette: light canvas, steel blue, and safety orange.
PALETTE = ["#315A78", "#E87524", "#6D8798", "#D6A23A", "#4E8B76", "#A9B8C2"]
CRITICALITY_COLORS = {
    "Critical": "#C0392B",
    "High": "#E87524",
    "Medium": "#D6A23A",
    "Low": "#4E8B76",
}

st.markdown(
    """
    <style>
    :root { color-scheme: light; }

    /* ---------- Global theme ---------- */
    .stApp {
        background: #F3F6FA;
        color: #1E293B;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4 {
        color: #16324F !important;
        font-weight: 700 !important;
        letter-spacing: -0.4px;
    }

    p, li, label,
    [data-testid="stMarkdownContainer"],
    [data-testid="stWidgetLabel"],
    [data-testid="stCaptionContainer"] {
        color: #475569;
    }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        background: #E8EEF5;
        border-right: 1px solid #D5DEE9;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        color: #16324F !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background: #315A78 !important;
        border: none !important;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] span {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] input {
        color: #203B50 !important;
    }

    /* ---------- KPI cards ---------- */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #DCE5EE;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 14px rgba(22, 50, 79, 0.05);
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {
        color: #64748B !important;
        font-size: 0.88rem !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {
        color: #16324F !important;
        font-weight: 700 !important;
    }

    /* ---------- Warning banner ---------- */
    [data-testid="stAlert"] {
        background: #FFF4DF !important;
        border: 1px solid #F1D49A !important;
        border-radius: 10px;
    }

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span,
    [data-testid="stAlert"] div {
        color: #754C0E !important;
    }

    /* ---------- Charts and tables ---------- */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid #DCE5EE;
        border-radius: 10px;
        overflow: hidden;
        background: #FFFFFF;
    }

    [data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        border: 1px solid #E1E8F0;
        border-radius: 14px;
        padding: 10px;
        box-shadow: 0 3px 12px rgba(22, 50, 79, 0.035);
    }

    /* ---------- Download button ---------- */
    .stDownloadButton button {
        background: #16324F !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9px !important;
        padding: 0.6rem 1rem;
        font-weight: 600;
    }

    .stDownloadButton button:hover {
        background: #E87524 !important;
        color: #FFFFFF !important;
    }

    /* ---------- Dividers and responsive spacing ---------- */
    hr {
        border-color: #DCE5EE !important;
    }

    [data-testid="stCaptionContainer"] {
        color: #64748B !important;
    }

    @media (max-width: 900px) {
        .block-container {
            padding: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    """Load the bundled synthetic CSV data."""
    required_files = {
        "equipment": "equipment.csv",
        "failures": "failure_events.csv",
        "inspections": "inspections.csv",
        "maintenance": "maintenance_records.csv",
        "work_orders": "work_orders.csv",
    }
    loaded = {}
    missing = []
    for key, filename in required_files.items():
        path = DATA / filename
        if not path.exists():
            missing.append(str(path))
        else:
            loaded[key] = pd.read_csv(path)

    if missing:
        raise FileNotFoundError(
            "Could not find these data files:\n" + "\n".join(missing)
        )

    for frame_name, date_columns in {
        "failures": ["failure_timestamp"],
        "inspections": ["inspection_date"],
        "maintenance": ["maintenance_date"],
        "work_orders": ["created_date", "closed_date"],
        "equipment": ["commissioned_date"],
    }.items():
        for column in date_columns:
            if column in loaded[frame_name].columns:
                loaded[frame_name][column] = pd.to_datetime(
                    loaded[frame_name][column], errors="coerce"
                )

    for frame_name, numeric_columns in {
        "failures": ["downtime_hours", "estimated_impact_cost"],
        "maintenance": ["duration_hours", "maintenance_cost"],
    }.items():
        for column in numeric_columns:
            if column in loaded[frame_name].columns:
                loaded[frame_name][column] = pd.to_numeric(
                    loaded[frame_name][column], errors="coerce"
                ).fillna(0)

    return loaded


def style_chart(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", color="#34495E"),
        title=dict(x=0.02, xanchor="left", font=dict(size=16, color="#203B50")),
        margin=dict(l=12, r=12, t=60, b=12),
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#E2E8ED", zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig


try:
    data = load_data()
except Exception as exc:
    st.error("The dashboard could not load its CSV data.")
    st.exception(exc)
    st.stop()

equipment = data["equipment"].copy()
failures = data["failures"].copy()
inspections = data["inspections"].copy()
maintenance = data["maintenance"].copy()
work_orders = data["work_orders"].copy()

# Normalize text fields to avoid filter mismatches caused by whitespace.
for frame, columns in [
    (equipment, ["plant_area", "criticality", "equipment_type", "equipment_name"]),
    (failures, ["failure_type", "severity"]),
    (maintenance, ["maintenance_type"]),
    (inspections, ["condition_rating"]),
    (work_orders, ["priority", "status"]),
]:
    for column in columns:
        if column in frame.columns:
            frame[column] = frame[column].fillna("Unknown").astype(str).str.strip()

# ---------------------------- Header ----------------------------
st.title("🏭 PlantPulse")
st.caption(
    "Industrial Reliability & Maintenance Analytics  |  "
    "Explore synthetic failure, downtime, inspection, and maintenance records."
)
st.warning(
    "Demo limitation: all bundled records are synthetic. "
    "Costs are illustrative, and recorded downtime is not equipment availability."
)

# ---------------------------- Sidebar filters ----------------------------
st.sidebar.title("Dashboard filters")
st.sidebar.caption("Choose the records included in the dashboard.")

areas = sorted(equipment["plant_area"].dropna().unique().tolist())
criticalities = sorted(equipment["criticality"].dropna().unique().tolist())
equipment_types = sorted(equipment["equipment_type"].dropna().unique().tolist())

selected_areas = st.sidebar.multiselect("Plant area", areas, default=areas)
selected_criticalities = st.sidebar.multiselect(
    "Equipment criticality", criticalities, default=criticalities
)
selected_types = st.sidebar.multiselect(
    "Equipment type", equipment_types, default=equipment_types
)

date_min = failures["failure_timestamp"].min()
date_max = failures["failure_timestamp"].max()
if pd.isna(date_min) or pd.isna(date_max):
    selected_dates = None
    st.sidebar.info("Failure timestamps are unavailable; date filtering is disabled.")
else:
    selected_dates = st.sidebar.date_input(
        "Failure date range",
        value=(date_min.date(), date_max.date()),
        min_value=date_min.date(),
        max_value=date_max.date(),
    )

filtered_equipment = equipment[
    equipment["plant_area"].isin(selected_areas)
    & equipment["criticality"].isin(selected_criticalities)
    & equipment["equipment_type"].isin(selected_types)
].copy()

selected_ids = filtered_equipment["equipment_id"].tolist()

f = failures[failures["equipment_id"].isin(selected_ids)].copy()
m = maintenance[maintenance["equipment_id"].isin(selected_ids)].copy()
i = inspections[inspections["equipment_id"].isin(selected_ids)].copy()
w = work_orders[work_orders["equipment_id"].isin(selected_ids)].copy()

if selected_dates and isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    f = f[
        f["failure_timestamp"].dt.date.between(start_date, end_date)
    ].copy()

# ---------------------------- KPI cards ----------------------------
total_equipment = len(filtered_equipment)
failure_count = len(f)
recorded_downtime = float(f["downtime_hours"].sum()) if not f.empty else 0.0
maintenance_spend = float(m["maintenance_cost"].sum()) if not m.empty else 0.0
open_orders_count = int(
    w["status"].isin(["Open", "In Progress", "On Hold"]).sum()
) if not w.empty else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Equipment in scope", f"{total_equipment:,}")
k2.metric("Recorded failure events", f"{failure_count:,}")
k3.metric("Recorded downtime", f"{recorded_downtime:,.1f} h")
k4.metric("Recorded maintenance spend", f"₹{maintenance_spend:,.0f}")
k5.metric("Active work orders", f"{open_orders_count:,}")

st.divider()

# ---------------------------- Trends and failure patterns ----------------------------
left, right = st.columns(2, gap="large")

with left:
    st.markdown("### 📈 Monthly recorded failures")
    if f.empty:
        st.info("No failure records match these filters.")
    else:
        monthly = (
            f.assign(month=f["failure_timestamp"].dt.to_period("M").dt.to_timestamp())
            .groupby("month", as_index=False)
            .agg(failure_events=("failure_id", "count"))
            .sort_values("month")
        )
        fig = px.line(
            monthly,
            x="month",
            y="failure_events",
            markers=True,
            title="Failure events by month",
            labels={"month": "Month", "failure_events": "Recorded events"},
            color_discrete_sequence=[PALETTE[0]],
        )
        st.plotly_chart(style_chart(fig, 360), use_container_width=True)

with right:
    st.markdown("### 🧰 Most frequent failure types")
    if f.empty:
        st.info("No failure records match these filters.")
    else:
        failure_types = (
            f.groupby("failure_type", as_index=False)
            .agg(events=("failure_id", "count"))
            .sort_values("events", ascending=False)
            .head(10)
        )
        fig = px.bar(
            failure_types,
            x="events",
            y="failure_type",
            orientation="h",
            title="Top failure types by event count",
            labels={"events": "Recorded events", "failure_type": "Failure type"},
            color_discrete_sequence=[PALETTE[1]],
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(style_chart(fig, 360), use_container_width=True)

st.divider()

# ---------------------------- Downtime and maintenance spend ----------------------------
left, right = st.columns(2, gap="large")

with left:
    st.markdown("### ⏱️ Top 10 equipment by downtime")
    if f.empty or filtered_equipment.empty:
        st.info("No failure records match these filters.")
    else:
        top_downtime = (
            f.groupby("equipment_id", as_index=False)
            .agg(downtime_hours=("downtime_hours", "sum"))
            .merge(
                filtered_equipment[
                    ["equipment_id", "equipment_name", "criticality"]
                ],
                on="equipment_id",
                how="left",
            )
            .sort_values("downtime_hours", ascending=False)
            .head(10)
        )
        fig = px.bar(
            top_downtime,
            x="downtime_hours",
            y="equipment_name",
            orientation="h",
            color="criticality",
            color_discrete_map=CRITICALITY_COLORS,
            hover_data={
                "downtime_hours": ":.1f",
                "equipment_name": True,
                "criticality": True,
            },
            title="Top 10 equipment by recorded downtime",
            labels={
                "downtime_hours": "Downtime (hours)",
                "equipment_name": "Equipment",
                "criticality": "Criticality",
            },
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(style_chart(fig, 380), use_container_width=True)

with right:
    st.markdown("### 💰 Maintenance spend by type")
    if m.empty:
        st.info("No maintenance records match these filters.")
    else:
        spend = (
            m.groupby("maintenance_type", as_index=False)
            .agg(
                jobs=("maintenance_id", "count"),
                maintenance_cost=("maintenance_cost", "sum"),
            )
            .sort_values("maintenance_cost", ascending=False)
        )
        fig = px.pie(
            spend,
            names="maintenance_type",
            values="maintenance_cost",
            hole=0.52,
            title="Share of recorded maintenance spend",
            color_discrete_sequence=PALETTE,
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            marker=dict(line=dict(color="#FFFFFF", width=2)),
        )
        st.plotly_chart(style_chart(fig, 380), use_container_width=True)

st.divider()

# ---------------------------- Latest inspection conditions ----------------------------
st.markdown("### 🔎 Latest inspection conditions")
if i.empty:
    st.info("No inspection records match these filters.")
else:
    latest = (
        i.sort_values(["inspection_date", "inspection_id"])
        .groupby("equipment_id", as_index=False)
        .tail(1)
    )
    latest = latest.merge(
        filtered_equipment[
            [
                "equipment_id",
                "equipment_name",
                "equipment_type",
                "criticality",
                "plant_area",
            ]
        ],
        on="equipment_id",
        how="left",
    )
    order = {"Critical": 0, "Poor": 1, "Monitor": 2, "Good": 3}
    latest["_order"] = latest["condition_rating"].map(order).fillna(4)
    latest = latest.sort_values(["_order", "inspection_date"], ascending=[True, False])
    st.dataframe(
        latest[
            [
                "equipment_id",
                "equipment_name",
                "equipment_type",
                "plant_area",
                "criticality",
                "inspection_date",
                "condition_rating",
                "finding",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

# ---------------------------- High-priority active work orders ----------------------------
st.markdown("### 🚨 High-priority open work orders")
active = w[
    (w["status"].isin(["Open", "In Progress", "On Hold"]))
    & (w["priority"].isin(["High", "Urgent"]))
].merge(
    filtered_equipment[
        ["equipment_id", "equipment_name", "plant_area", "criticality"]
    ],
    on="equipment_id",
    how="left",
)

if active.empty:
    st.success("No high-priority active work orders match the current scope.")
else:
    priority_order = {"Urgent": 0, "High": 1}
    active["_priority_order"] = active["priority"].map(priority_order).fillna(2)
    active = active.sort_values(
        ["_priority_order", "created_date"], ascending=[True, True]
    )
    st.dataframe(
        active[
            [
                "work_order_id",
                "equipment_name",
                "plant_area",
                "criticality",
                "priority",
                "status",
                "created_date",
                "description",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

# ---------------------------- Download and notes ----------------------------
st.download_button(
    "⬇️ Download filtered failure events (CSV)",
    data=f.to_csv(index=False).encode("utf-8"),
    file_name="filtered_failure_events.csv",
    mime="text/csv",
)

with st.expander("How to interpret this dashboard"):
    st.markdown(
        """
        - Counts and totals describe only the synthetic records included in this demo.
        - Recorded downtime is not equivalent to equipment availability unless operating-time exposure is known.
        - Estimated impact cost is illustrative synthetic data, not measured financial loss.
        - Criticality is a supplied category, not a model-generated risk score.
        - Use the dashboard to explore records, not to make operational maintenance decisions.
        """
    )

st.caption("PlantPulse · Portfolio demonstration · Synthetic data only")
