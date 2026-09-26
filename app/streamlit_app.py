"""
Care Transition Efficiency & Placement Outcome Analytics
=========================================================

Interactive Streamlit dashboard for analyzing UAC care pipeline efficiency,
backlog dynamics, and placement outcomes.

Data source: HHS Unaccompanied Alien Children Program daily reports.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import pandas as pd
import streamlit as st

from src.data.load import load_data
from src.data.validation import validate
from src.analytics.pipeline import compute_pipeline_summary, compute_daily_pipeline, compute_net_flow
from src.analytics.efficiency import compute_all_kpis, compute_kpi_summary
from src.analytics.backlog import (
    compute_inflow_outflow,
    compute_cumulative_backlog,
    detect_backlog_periods,
)
from src.visualization.charts import (
    plot_pipeline_flow,
    plot_pipeline_sankey,
    plot_kpi_timeseries,
    plot_inflow_outflow,
    plot_backlog_cumulative,
    plot_weekday_heatmap,
    plot_monthly_trends,
    plot_discharge_stability,
    plot_outcome_trends,
)


# -----------------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Care Transition Efficiency & Placement Outcome Analytics",
    layout="wide",
    page_icon="📊",
)

st.title("Care Transition Efficiency & Placement Outcome Analytics")
st.markdown(
    """
    Analyzing the UAC care pipeline: **CBP Custody → HHS Care → Sponsor Placement**

    This dashboard monitors transition efficiency, backlog dynamics, and placement outcomes.
    """
)


# -----------------------------------------------------------------------------
# Data loading (cached)
# -----------------------------------------------------------------------------
@st.cache_data
def get_data():
    """Load and validate the UAC dataset."""
    df = load_data()
    validation_report = validate(df)
    return df, validation_report


df, validation_report = get_data()

if df.empty:
    st.error("No data loaded. Please check that the dataset exists in `data/raw/`.")
    st.stop()


# -----------------------------------------------------------------------------
# Sidebar: Controls
# -----------------------------------------------------------------------------
st.sidebar.header("Dashboard Controls")

# Date range selection
date_min = df["date"].min().date()
date_max = df["date"].max().date()

st.sidebar.subheader("Date Range")
start_date = st.sidebar.date_input(
    "Start Date",
    value=date_min,
    min_value=date_min,
    max_value=date_max,
    help="Select the start of the reporting period.",
)
end_date = st.sidebar.date_input(
    "End Date",
    value=date_max,
    min_value=date_min,
    max_value=date_max,
    help="Select the end of the reporting period.",
)

if start_date > end_date:
    st.sidebar.error("Start date must be before or equal to end date.")
    st.stop()

# Filter data by date range
mask = (df["date"] >= pd.Timestamp(start_date)) & (df["date"] <= pd.Timestamp(end_date))
df_filtered = df.loc[mask].reset_index(drop=True)

if df_filtered.empty:
    st.warning(f"No data available for the selected date range: {start_date} to {end_date}.")
    st.stop()

# Metric toggles
st.sidebar.subheader("Metric Toggles")
show_transfer_efficiency = st.sidebar.checkbox("Show Transfer Efficiency Ratio", value=True)
show_discharge_effectiveness = st.sidebar.checkbox("Show Discharge Effectiveness", value=True)
show_pipeline_throughput = st.sidebar.checkbox("Show Pipeline Throughput", value=True)
show_backlog_rate = st.sidebar.checkbox("Show Backlog Accumulation Rate", value=True)
show_outcome_stability = st.sidebar.checkbox("Show Outcome Stability Score", value=True)

# Alert thresholds
st.sidebar.subheader("Alert Thresholds")
st.sidebar.caption("_Analytical thresholds, not official policy_")

transfer_threshold = st.sidebar.number_input(
    "Transfer Efficiency Warning",
    min_value=0.0,
    max_value=1.0,
    value=0.3,
    step=0.05,
    help="Flag when transfer efficiency falls below this value.",
)
discharge_threshold = st.sidebar.number_input(
    "Discharge Effectiveness Warning",
    min_value=0.0,
    max_value=0.1,
    value=0.005,
    step=0.001,
    format="%.4f",
    help="Flag when discharge effectiveness falls below this value.",
)
backlog_alert = st.sidebar.number_input(
    "Backlog Alert (net daily surplus)",
    min_value=0,
    max_value=500,
    value=20,
    step=5,
    help="Flag when average daily backlog accumulation exceeds this value.",
)


# -----------------------------------------------------------------------------
# Compute analytics
# -----------------------------------------------------------------------------
kpis = compute_all_kpis(df_filtered)
kpi_summary = compute_kpi_summary(df_filtered)
pipeline_summary = compute_pipeline_summary(df_filtered)
inflow_outflow = compute_inflow_outflow(df_filtered)
cumulative_backlog = compute_cumulative_backlog(df_filtered)
backlog_periods = detect_backlog_periods(df_filtered, threshold_days=7)

# Prior period comparison (for delta calculations)
period_days = len(df_filtered)
prior_end = pd.Timestamp(start_date) - pd.Timedelta(days=1)
prior_start = prior_end - pd.Timedelta(days=period_days)
mask_prior = (df["date"] >= prior_start) & (df["date"] <= prior_end)
df_prior = df.loc[mask_prior]

if not df_prior.empty:
    prior_kpi_summary = compute_kpi_summary(df_prior)
    has_prior = True
else:
    prior_kpi_summary = {}
    has_prior = False


# -----------------------------------------------------------------------------
# Section 1: KPI Summary Cards
# -----------------------------------------------------------------------------
st.header("Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

# Helper for delta calculation
def get_delta(current, prior_key):
    if not has_prior or prior_key not in prior_kpi_summary:
        return None
    prior = prior_kpi_summary.get(prior_key, 0)
    if prior == 0:
        return None
    return round(current - prior, 4)


# Transfer Efficiency
with col1:
    if show_transfer_efficiency:
        val = kpi_summary["transfer_efficiency"]
        delta = get_delta(val, "transfer_efficiency")
        st.metric(
            "Transfer Efficiency Ratio",
            value=f"{val:.3f}",
            delta=delta,
            delta_color="normal" if (delta is None or delta >= 0) else "inverse",
            help="Transfers ÷ CBP Custody. Higher = faster CBP→HHS movement.",
        )
        if val < transfer_threshold:
            st.warning(f"⚠️ Below threshold ({transfer_threshold:.2f})")

# Discharge Effectiveness
with col2:
    if show_discharge_effectiveness:
        val = kpi_summary["discharge_effectiveness"]
        delta = get_delta(val, "discharge_effectiveness")
        st.metric(
            "Discharge Effectiveness",
            value=f"{val:.4f}",
            delta=delta,
            delta_color="normal" if (delta is None or delta >= 0) else "inverse",
            help="Discharges ÷ HHS Care. Higher = more effective placement.",
        )
        if val < discharge_threshold:
            st.warning(f"⚠️ Below threshold ({discharge_threshold:.4f})")

# Pipeline Throughput
with col3:
    if show_pipeline_throughput:
        val = kpi_summary["pipeline_throughput"]
        delta = get_delta(val, "pipeline_throughput")
        st.metric(
            "Pipeline Throughput",
            value=f"{val:.3f}",
            delta=delta,
            delta_color="normal" if (delta is None or delta >= 0) else "inverse",
            help="7-day rolling exits ÷ entries. ≥1.0 = exits keep pace.",
        )

# Backlog Accumulation Rate
with col4:
    if show_backlog_rate:
        val = kpi_summary["backlog_accumulation"]
        delta = get_delta(val, "backlog_accumulation")
        st.metric(
            "Backlog Accumulation Rate",
            value=f"{val:.2f}",
            delta=delta,
            delta_color="inverse" if (delta is None or delta <= 0) else "normal",
            help="Avg daily net inflow (7-day rolling). Positive = backlog building.",
        )
        if val > backlog_alert:
            st.error(f"🚨 Backlog alert: {val:.1f} > {backlog_alert} threshold")

# Outcome Stability Score
with col5:
    if show_outcome_stability:
        val = kpi_summary["outcome_stability"]
        delta = get_delta(val, "outcome_stability")
        st.metric(
            "Outcome Stability Score",
            value=f"{val:.3f}",
            delta=delta,
            delta_color="normal" if (delta is None or delta >= 0) else "inverse",
            help="1 − CV of discharges (14-day). Near 1.0 = stable placements.",
        )

st.markdown("---")


# -----------------------------------------------------------------------------
# Section 2: Care Pipeline Flow
# -----------------------------------------------------------------------------
st.header("Care Pipeline Flow")

tab_timeline, tab_sankey = st.tabs(["Pipeline Timeline", "Pipeline Sankey"])

with tab_timeline:
    try:
        fig_flow = plot_pipeline_flow(df_filtered)
        st.plotly_chart(fig_flow, use_container_width=True)
    except Exception as e:
        st.error(f"Could not render pipeline timeline: {e}")

with tab_sankey:
    try:
        sankey_summary = {
            "total_apprehended": pipeline_summary["total_intake"],
            "total_transferred": pipeline_summary["total_transfers"],
            "total_discharged": pipeline_summary["total_discharges"],
        }
        fig_sankey = plot_pipeline_sankey(sankey_summary)
        st.plotly_chart(fig_sankey, use_container_width=True)
        st.caption(
            f"Aggregate flows over selected period: {start_date} to {end_date}"
        )
    except Exception as e:
        st.error(f"Could not render Sankey diagram: {e}")

st.markdown("---")


# -----------------------------------------------------------------------------
# Section 3: Transfer & Discharge Efficiency
# -----------------------------------------------------------------------------
st.header("Transfer & Discharge Efficiency")

col_left, col_right = st.columns(2)

with col_left:
    if show_transfer_efficiency:
        try:
            fig_te = plot_kpi_timeseries(
                kpis, "transfer_efficiency", threshold=transfer_threshold
            )
            st.plotly_chart(fig_te, use_container_width=True)
        except Exception as e:
            st.error(f"Could not render Transfer Efficiency chart: {e}")

with col_right:
    if show_discharge_effectiveness:
        try:
            fig_de = plot_kpi_timeseries(
                kpis, "discharge_effectiveness", threshold=discharge_threshold
            )
            st.plotly_chart(fig_de, use_container_width=True)
        except Exception as e:
            st.error(f"Could not render Discharge Effectiveness chart: {e}")

if show_pipeline_throughput:
    try:
        fig_pt = plot_kpi_timeseries(kpis, "pipeline_throughput", threshold=1.0)
        st.plotly_chart(fig_pt, use_container_width=True)
    except Exception as e:
        st.error(f"Could not render Pipeline Throughput chart: {e}")

st.markdown("---")


# -----------------------------------------------------------------------------
# Section 4: Bottleneck & Backlog Analysis
# -----------------------------------------------------------------------------
st.header("Bottleneck & Backlog Analysis")

try:
    fig_inflow_outflow = plot_inflow_outflow(df_filtered)
    st.plotly_chart(fig_inflow_outflow, use_container_width=True)
except Exception as e:
    st.error(f"Could not render Inflow vs Outflow chart: {e}")

try:
    fig_backlog = plot_backlog_cumulative(cumulative_backlog)
    st.plotly_chart(fig_backlog, use_container_width=True)
except Exception as e:
    st.error(f"Could not render Cumulative Backlog chart: {e}")

with st.expander("📋 Detected Backlog Periods (≥7 consecutive days of net inflow)"):
    if backlog_periods.empty:
        st.info("No sustained backlog periods detected in the selected date range.")
    else:
        st.dataframe(
            backlog_periods.style.format(
                {
                    "start_date": lambda x: x.strftime("%Y-%m-%d"),
                    "end_date": lambda x: x.strftime("%Y-%m-%d"),
                    "total_surplus": "{:,}",
                    "avg_daily_surplus": "{:.1f}",
                }
            ),
            use_container_width=True,
        )

st.markdown("---")


# -----------------------------------------------------------------------------
# Section 5: Outcome Trends & Stability
# -----------------------------------------------------------------------------
st.header("Outcome Trends & Stability")

# Monthly aggregation for trends
df_filtered_monthly = df_filtered.copy()
df_filtered_monthly["year_month"] = df_filtered_monthly["date"].dt.to_period("M")
monthly = (
    df_filtered_monthly.groupby("year_month")
    .agg(
        cbp_apprehended=("cbp_apprehended", "sum"),
        cbp_transferred=("cbp_transferred", "sum"),
        hhs_discharged=("hhs_discharged", "sum"),
    )
    .reset_index()
)
monthly["month"] = monthly["year_month"].astype(str)
monthly["discharge_pct_change"] = monthly["hhs_discharged"].pct_change() * 100

# Weekday patterns
df_filtered["day_of_week"] = df_filtered["date"].dt.day_name()
weekday_stats = (
    df_filtered.groupby("day_of_week")
    .agg(
        cbp_apprehended=("cbp_apprehended", "mean"),
        cbp_transferred=("cbp_transferred", "mean"),
        hhs_discharged=("hhs_discharged", "mean"),
    )
    .reset_index()
)

# Discharge variability
variability = kpis[["date"]].copy()
variability["discharge_rolling_mean"] = (
    df_filtered["hhs_discharged"].rolling(14, min_periods=1).mean()
)
variability["discharge_rolling_std"] = (
    df_filtered["hhs_discharged"].rolling(14, min_periods=1).std()
)
variability["discharge_cv"] = (
    variability["discharge_rolling_std"] / variability["discharge_rolling_mean"]
).fillna(0)

col_trends, col_stability = st.columns(2)

with col_trends:
    try:
        fig_monthly = plot_outcome_trends(monthly)
        st.plotly_chart(fig_monthly, use_container_width=True)
    except Exception as e:
        st.error(f"Could not render Outcome Trends chart: {e}")

with col_stability:
    try:
        fig_stability = plot_discharge_stability(variability)
        st.plotly_chart(fig_stability, use_container_width=True)
    except Exception as e:
        st.error(f"Could not render Discharge Stability chart: {e}")

try:
    fig_weekday = plot_weekday_heatmap(weekday_stats)
    st.plotly_chart(fig_weekday, use_container_width=True)
except Exception as e:
    st.error(f"Could not render Weekday Heatmap: {e}")

# Sudden drops detection (days where discharge dropped >50% from rolling mean)
sudden_drops = df_filtered.copy()
sudden_drops["rolling_mean"] = sudden_drops["hhs_discharged"].rolling(7, min_periods=1).mean()
sudden_drops["pct_drop"] = (sudden_drops["hhs_discharged"] - sudden_drops["rolling_mean"]) / sudden_drops["rolling_mean"] * 100
drops_detected = sudden_drops[sudden_drops["pct_drop"] < -50][["date", "hhs_discharged", "rolling_mean", "pct_drop"]]

with st.expander("⚠️ Detected Sudden Drops (>50% below 7-day rolling mean)"):
    if drops_detected.empty:
        st.info("No sudden discharge drops detected in the selected date range.")
    else:
        drops_display = drops_detected.copy()
        drops_display["date"] = drops_display["date"].dt.strftime("%Y-%m-%d")
        drops_display = drops_display.rename(columns={
            "date": "Date",
            "hhs_discharged": "Discharges",
            "rolling_mean": "7-Day Mean",
            "pct_drop": "% Drop",
        })
        st.dataframe(
            drops_display.style.format({"Discharges": "{:.0f}", "7-Day Mean": "{:.1f}", "% Drop": "{:.1f}%"}),
            use_container_width=True,
        )

st.markdown("---")


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown(
    """
    <hr>
    <div style="text-align: center; color: #7f7f7f; font-size: 0.85em;">
        <strong>Data source:</strong> HHS Unaccompanied Alien Children Program daily reports<br>
        <strong>Analysis period:</strong> {start} to {end}<br>
        <em>Alert thresholds shown are analytical defaults, not official policy thresholds.</em>
    </div>
    """.format(start=start_date, end=end_date),
    unsafe_allow_html=True,
)
