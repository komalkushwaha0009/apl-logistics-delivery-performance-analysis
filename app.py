"""
APL Logistics — Delivery Performance, Delay Risk & Logistics Efficiency Dashboard
Run with:  streamlit run app.py
Requires:  pip install streamlit pandas plotly
Expects a cleaned CSV at ./cleaned_data.csv (or update DATA_PATH below).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import gzip
import shutil

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="APL Logistics | Delivery Performance Dashboard",
    page_icon="🚚",
    layout="wide",
)

DATA_PATH = "cleaned_data.csv"
DATA_PATH_GZ = "cleaned_data.csv.gz"

COLOR_MAP = {"On-time": "#2E86AB", "Delayed": "#E63946", "Early": "#6BAA75"}

# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path, gz_path):
    # Auto-decompress on first run (e.g. on Streamlit Cloud, where only the
    # compressed file is committed to keep the repo small).
    if not os.path.exists(path) and os.path.exists(gz_path):
        with gzip.open(gz_path, "rb") as f_in, open(path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    df = pd.read_csv(path)
    return df

try:
    df_raw = load_data(DATA_PATH, DATA_PATH_GZ)
except FileNotFoundError:
    st.error(
        f"Could not find `{DATA_PATH}` or `{DATA_PATH_GZ}`. Place the cleaned dataset "
        f"(produced by 01_clean_data.py) in the same folder as this app."
    )
    st.stop()

# ----------------------------------------------------------------------------
# SIDEBAR — FILTERS
# ----------------------------------------------------------------------------
st.sidebar.title("🚚 APL Logistics")
st.sidebar.caption("Delivery Performance & Delay Risk Dashboard")
st.sidebar.markdown("---")
st.sidebar.header("Filters")

shipping_modes = st.sidebar.multiselect(
    "Shipping Mode", sorted(df_raw["Shipping Mode"].unique()),
    default=sorted(df_raw["Shipping Mode"].unique()),
)
markets = st.sidebar.multiselect(
    "Market", sorted(df_raw["Market"].unique()),
    default=sorted(df_raw["Market"].unique()),
)
regions = st.sidebar.multiselect(
    "Order Region", sorted(df_raw["Order Region"].unique()),
    default=sorted(df_raw["Order Region"].unique()),
)
segments = st.sidebar.multiselect(
    "Customer Segment", sorted(df_raw["Customer Segment"].unique()),
    default=sorted(df_raw["Customer Segment"].unique()),
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "ℹ️ No order-date field exists in this dataset, so a date-range filter "
    "isn't available. All other required filters (mode, region, market, segment) are active."
)

df = df_raw[
    df_raw["Shipping Mode"].isin(shipping_modes)
    & df_raw["Market"].isin(markets)
    & df_raw["Order Region"].isin(regions)
    & df_raw["Customer Segment"].isin(segments)
]

if df.empty:
    st.warning("No orders match the selected filters. Adjust filters in the sidebar.")
    st.stop()

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.title("Delivery Performance, Delay Risk & Logistics Efficiency")
st.caption(
    f"Showing **{len(df):,}** of {len(df_raw):,} orders based on current filters"
)

tabs = st.tabs([
    "📊 Delivery Performance Overview",
    "⚠️ Delay Risk Analysis",
    "🚛 Shipping Mode Comparison",
    "🌍 Regional & Market Diagnostics",
])

# ----------------------------------------------------------------------------
# TAB 1 — Delivery Performance Overview
# ----------------------------------------------------------------------------
with tabs[0]:
    st.subheader("On-Time vs Late Delivery KPIs")

    total = len(df)
    on_time_pct = (df["Delivery_Classification"] == "On-time").mean() * 100
    delayed_pct = (df["Delivery_Classification"] == "Delayed").mean() * 100
    early_pct = (df["Delivery_Classification"] == "Early").mean() * 100
    avg_delay = df["Delay_Gap"].mean()
    late_risk = df["Late_delivery_risk"].mean() * 100

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Orders", f"{total:,}")
    c2.metric("On-Time Rate", f"{on_time_pct:.1f}%")
    c3.metric("Delayed Rate", f"{delayed_pct:.1f}%")
    c4.metric("Avg Delay Gap", f"{avg_delay:+.2f} days")
    c5.metric("Late Delivery Risk", f"{late_risk:.1f}%")

    col1, col2 = st.columns(2)
    with col1:
        counts = df["Delivery_Classification"].value_counts().reindex(["On-time", "Delayed", "Early"]).fillna(0)
        fig = px.bar(
            x=counts.index, y=counts.values,
            color=counts.index, color_discrete_map=COLOR_MAP,
            labels={"x": "Delivery Classification", "y": "Number of Orders"},
            title="Delivery Outcome Distribution",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.pie(
            values=counts.values, names=counts.index,
            color=counts.index, color_discrete_map=COLOR_MAP,
            title="Delivery Outcome Share", hole=0.45,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Financial Impact of Delivery Outcome")
    fin = df.groupby("Delivery_Classification")["Order Profit Per Order"].mean().reindex(["Early", "On-time", "Delayed"])
    fig3 = px.bar(
        x=fin.index, y=fin.values, color=fin.index, color_discrete_map=COLOR_MAP,
        labels={"x": "Delivery Classification", "y": "Avg Profit per Order ($)"},
        title="Average Order Profit by Delivery Outcome",
    )
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 2 — Delay Risk Analysis
# ----------------------------------------------------------------------------
with tabs[1]:
    st.subheader("Late Delivery Risk Distribution")

    col1, col2 = st.columns([1, 2])
    with col1:
        risk_counts = df["Late_delivery_risk"].value_counts().rename({0: "Not Late", 1: "Late"})
        fig = px.pie(
            values=risk_counts.values, names=risk_counts.index,
            color=risk_counts.index,
            color_discrete_map={"Late": "#E63946", "Not Late": "#2E86AB"},
            title="Late Delivery Risk Share", hole=0.45,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(
            df, x="Delay_Gap", nbins=11,
            title="Delay Gap Histogram (Actual − Scheduled Days)",
            labels={"Delay_Gap": "Delay Gap (days)"},
            color_discrete_sequence=["#457B9D"],
        )
        fig.add_vline(x=0, line_dash="dash", line_color="#E63946", annotation_text="On-time")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Late Delivery Risk by Product Category (Top 15 by volume)")
    cat = df.groupby("Category Name").agg(
        orders=("Delay_Gap", "count"),
        late_risk_pct=("Late_delivery_risk", lambda x: x.mean() * 100),
    )
    cat = cat[cat["orders"] >= 50].sort_values("orders", ascending=False).head(15)
    fig = px.bar(
        cat.sort_values("late_risk_pct"), x="late_risk_pct", y=cat.sort_values("late_risk_pct").index,
        orientation="h", labels={"late_risk_pct": "Late Risk (%)", "y": "Category"},
        color="late_risk_pct", color_continuous_scale="Reds",
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 3 — Shipping Mode Comparison
# ----------------------------------------------------------------------------
with tabs[2]:
    st.subheader("Shipping Mode Efficiency")

    mode_stats = df.groupby("Shipping Mode").agg(
        orders=("Delay_Gap", "count"),
        avg_delay_gap=("Delay_Gap", "mean"),
        late_risk_pct=("Late_delivery_risk", lambda x: x.mean() * 100),
        on_time_pct=("Delivery_Classification", lambda x: (x == "On-time").mean() * 100),
        avg_scheduled=("Days for shipment (scheduled)", "mean"),
        avg_actual=("Days for shipping (real)", "mean"),
    ).round(2).sort_values("late_risk_pct", ascending=False)

    st.dataframe(
        mode_stats.rename(columns={
            "orders": "Orders", "avg_delay_gap": "Avg Delay Gap",
            "late_risk_pct": "Late Risk %", "on_time_pct": "On-Time %",
            "avg_scheduled": "Avg Scheduled Days", "avg_actual": "Avg Actual Days",
        }),
        use_container_width=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            mode_stats, x=mode_stats.index, y="late_risk_pct",
            title="SLA Compliance Risk by Shipping Mode",
            labels={"late_risk_pct": "Late Risk (%)", "x": "Shipping Mode"},
            color="late_risk_pct", color_continuous_scale="Reds",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        plot_df = mode_stats.reset_index().melt(
            id_vars="Shipping Mode", value_vars=["avg_scheduled", "avg_actual"],
            var_name="Type", value_name="Days",
        )
        plot_df["Type"] = plot_df["Type"].map({"avg_scheduled": "Scheduled", "avg_actual": "Actual"})
        fig = px.bar(
            plot_df, x="Shipping Mode", y="Days", color="Type", barmode="group",
            title="Scheduled vs Actual Shipping Days by Mode",
            color_discrete_map={"Scheduled": "#8ECAE6", "Actual": "#FB8500"},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.info(
        "💡 **Key insight:** First Class orders are scheduled for 1 day but consistently "
        "take 2 days to fulfill — resulting in a 100% late rate. This is a fixed SLA "
        "design mismatch, not a variable operational issue."
    )

# ----------------------------------------------------------------------------
# TAB 4 — Regional & Market Diagnostics
# ----------------------------------------------------------------------------
with tabs[3]:
    st.subheader("Geographic Delay Visualization")

    geo = df.groupby(["Order Country", "Order Region"]).agg(
        orders=("Delay_Gap", "count"),
        late_risk_pct=("Late_delivery_risk", lambda x: x.mean() * 100),
        avg_lat=("Latitude", "mean"),
        avg_lon=("Longitude", "mean"),
    ).reset_index()
    geo = geo[geo["orders"] >= 20]

    fig = px.scatter_geo(
        geo, lat="avg_lat", lon="avg_lon", size="orders", color="late_risk_pct",
        color_continuous_scale="RdYlGn_r", hover_name="Order Country",
        hover_data={"avg_lat": False, "avg_lon": False, "orders": True, "late_risk_pct": ":.1f"},
        title="Late Delivery Risk by Country (bubble size = order volume)",
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        market_stats = df.groupby("Market").agg(
            orders=("Delay_Gap", "count"),
            late_risk_pct=("Late_delivery_risk", lambda x: x.mean() * 100),
        ).sort_values("late_risk_pct", ascending=False)
        fig = px.bar(
            market_stats, x=market_stats.index, y="late_risk_pct",
            title="Late Delivery Risk by Market",
            labels={"late_risk_pct": "Late Risk (%)", "x": "Market"},
            color="late_risk_pct", color_continuous_scale="Oranges",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        region_stats = df.groupby("Order Region").agg(
            orders=("Delay_Gap", "count"),
            late_risk_pct=("Late_delivery_risk", lambda x: x.mean() * 100),
        ).sort_values("late_risk_pct", ascending=False).head(15)
        fig = px.bar(
            region_stats.sort_values("late_risk_pct"),
            x="late_risk_pct", y=region_stats.sort_values("late_risk_pct").index,
            orientation="h", title="Late Delivery Risk by Region (Top 15)",
            labels={"late_risk_pct": "Late Risk (%)", "y": "Region"},
            color="late_risk_pct", color_continuous_scale="Purples",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Note: Regional and market-level risk is comparatively flat (roughly 55%–70% "
        "across the board) versus the shipping-mode effect seen in the previous tab — "
        "geography is a secondary factor in this dataset."
    )

st.markdown("---")
st.caption(
    "APL Logistics (KWE Group) · Delivery Performance, Delay Risk & Logistics Efficiency Analysis "
    "· Unified Mentor Data Analytics Internship Project"
)
