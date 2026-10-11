                "downtime_hours": "Downtime (hours)",
                "equipment_name": "Equipment",
                "criticality": "Criticality",
            },
            title="Top 10 equipment by recorded downtime",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        fig = style_chart(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)

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
        fig = style_chart(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)

st.divider()
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
        ].sort_values(["priority", "created_date"], ascending=[True, True]),
        use_container_width=True,
        hide_index=True,
    )

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
        - The estimated impact cost is illustrative synthetic data, not measured financial loss.