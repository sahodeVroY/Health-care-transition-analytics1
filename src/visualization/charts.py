"""
Visualization module for Care Transition Efficiency & Placement Outcome Analytics.

All chart functions return Plotly Figure objects with a consistent
professional color palette and responsive layout.

Color scheme
------------
- CBP-related : #1f77b4 (blue)
- HHS-related : #ff7f0e (orange)
- Discharge/placement : #2ca02c (green)
- Alerts/negative : #d62728 (red)
- Neutral : #7f7f7f (gray)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ── Palette ──────────────────────────────────────────────────────────────────
COLOR_CBP = "#1f77b4"
COLOR_HHS = "#ff7f0e"
COLOR_DISCHARGE = "#2ca02c"
COLOR_ALERT = "#d62728"
COLOR_NEUTRAL = "#7f7f7f"

_COMMON_LAYOUT = dict(
    template="plotly_white",
    margin=dict(l=50, r=30, t=50, b=40),
    hovermode="x unified",
    font=dict(family="Arial, sans-serif", size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)


def _apply_layout(fig: go.Figure, **overrides: Any) -> go.Figure:
    """Merge the common layout with per-chart overrides."""
    layout = {**_COMMON_LAYOUT, **overrides}
    fig.update_layout(**layout)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 1. Pipeline Flow — Stacked Area
# ─────────────────────────────────────────────────────────────────────────────
def plot_pipeline_flow(df: pd.DataFrame) -> go.Figure:
    """Stacked area chart of CBP custody and HHS care stocks over time.

    Parameters
    ----------
    df : DataFrame with columns ``date``, ``cbp_custody``, ``hhs_care``.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["cbp_custody"],
            name="CBP Custody",
            mode="lines",
            fill="tozeroy",
            line=dict(color=COLOR_CBP, width=1),
            fillcolor="rgba(31,119,180,0.3)",
            hovertemplate="CBP Custody: %{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["hhs_care"],
            name="HHS Care",
            mode="lines",
            fill="tozeroy",
            line=dict(color=COLOR_HHS, width=1),
            fillcolor="rgba(255,127,14,0.3)",
            hovertemplate="HHS Care: %{y:,.0f}<extra></extra>",
        )
    )
    return _apply_layout(
        fig,
        title="Care Pipeline: Active Caseloads Over Time",
        xaxis_title="Date",
        yaxis_title="Children",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Pipeline Sankey Diagram
# ─────────────────────────────────────────────────────────────────────────────
def plot_pipeline_sankey(summary: Dict[str, float]) -> go.Figure:
    """Sankey diagram of aggregate pipeline flows.

    Parameters
    ----------
    summary : dict with keys ``total_apprehended``, ``total_transferred``,
              ``total_discharged``, and optionally ``avg_cbp_custody`` /
              ``avg_hhs_care``.
    """
    labels = ["CBP Intake", "CBP Custody", "HHS Care", "Sponsor Placement"]
    source = [0, 1, 2]
    target = [1, 2, 3]
    values = [
        summary.get("total_apprehended", 0),
        summary.get("total_transferred", 0),
        summary.get("total_discharged", 0),
    ]
    colors = [COLOR_CBP, COLOR_HHS, COLOR_DISCHARGE]

    fig = go.Figure(
        go.Sankey(
            arrangement="snap",
            node=dict(
                pad=20,
                thickness=25,
                line=dict(color="black", width=0.5),
                label=labels,
                color=[COLOR_CBP, COLOR_CBP, COLOR_HHS, COLOR_DISCHARGE],
            ),
            link=dict(source=source, target=target, value=values, color=colors),
        )
    )
    return _apply_layout(fig, title="Care Pipeline Flow (Aggregate)")


# ─────────────────────────────────────────────────────────────────────────────
# 3. KPI Time-Series
# ─────────────────────────────────────────────────────────────────────────────
def plot_kpi_timeseries(
    kpi_df: pd.DataFrame,
    metric_name: str,
    title: Optional[str] = None,
    threshold: Optional[float] = None,
) -> go.Figure:
    """Line chart for a single KPI over time.

    Parameters
    ----------
    kpi_df : DataFrame with a ``date`` column and the KPI column.
    metric_name : Column name of the KPI to plot.
    title : Chart title; defaults to the ``metric_name`` in title-case.
    threshold : Optional horizontal reference line.
    """
    display_title = title or metric_name.replace("_", " ").title()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=kpi_df["date"],
            y=kpi_df[metric_name],
            name=display_title,
            mode="lines+markers",
            marker=dict(size=3),
            line=dict(color=COLOR_CBP, width=2),
            hovertemplate=f"{display_title}: %{{y:.3f}}<extra></extra>",
        )
    )
    if threshold is not None:
        fig.add_hline(
            y=threshold,
            line_dash="dash",
            line_color=COLOR_ALERT,
            annotation_text=f"Threshold ({threshold:.2f})",
            annotation_position="top left",
        )
    return _apply_layout(fig, title=display_title, xaxis_title="Date", yaxis_title=display_title)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Inflow vs. Outflow
# ─────────────────────────────────────────────────────────────────────────────
def plot_inflow_outflow(df: pd.DataFrame) -> go.Figure:
    """Dual line chart of daily CBP apprehensions vs. HHS discharges.

    Shaded red where inflow > outflow; shaded green where outflow > inflow.

    Parameters
    ----------
    df : DataFrame with columns ``date``, ``cbp_apprehended``, ``hhs_discharged``.
    """
    inflow = df["cbp_apprehended"].values
    outflow = df["hhs_discharged"].values
    dates = df["date"].values

    fig = go.Figure()

    # Shade regions -----------------------------------------------------------
    upper = np.maximum(inflow, outflow)
    # Red: inflow exceeds outflow
    red_fill = np.where(inflow > outflow, upper, outflow)
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([dates, dates[::-1]]),
            y=np.concatenate([inflow, np.minimum(inflow, outflow)[::-1]]),
            fill="toself",
            fillcolor="rgba(214,39,40,0.15)",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
            name="Inflow > Outflow",
        )
    )
    # Green: outflow exceeds inflow
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([dates, dates[::-1]]),
            y=np.concatenate([outflow, np.minimum(inflow, outflow)[::-1]]),
            fill="toself",
            fillcolor="rgba(44,160,44,0.15)",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
            name="Outflow > Inflow",
        )
    )

    # Lines -------------------------------------------------------------------
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=inflow,
            name="CBP Apprehensions (Inflow)",
            mode="lines",
            line=dict(color=COLOR_CBP, width=2),
            hovertemplate="Inflow: %{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=outflow,
            name="HHS Discharges (Outflow)",
            mode="lines",
            line=dict(color=COLOR_DISCHARGE, width=2),
            hovertemplate="Outflow: %{y:,.0f}<extra></extra>",
        )
    )
    return _apply_layout(
        fig,
        title="Pipeline Inflow vs. Outflow",
        xaxis_title="Date",
        yaxis_title="Children per Day",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5. Cumulative Backlog
# ─────────────────────────────────────────────────────────────────────────────
def plot_backlog_cumulative(backlog_df: pd.DataFrame) -> go.Figure:
    """Area chart of cumulative backlog (red positive, green negative).

    Parameters
    ----------
    backlog_df : DataFrame with columns ``date`` and ``cumulative_backlog``.
    """
    dates = backlog_df["date"]
    values = backlog_df["cumulative_backlog"]

    fig = go.Figure()

    pos = values.clip(lower=0)
    neg = values.clip(upper=0)

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=pos,
            fill="tozeroy",
            name="Backlog Growing",
            line=dict(color=COLOR_ALERT, width=1),
            fillcolor="rgba(214,39,40,0.25)",
            hovertemplate="Backlog: +%{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=neg,
            fill="tozeroy",
            name="Backlog Clearing",
            line=dict(color=COLOR_DISCHARGE, width=1),
            fillcolor="rgba(44,160,44,0.25)",
            hovertemplate="Backlog: %{y:,.0f}<extra></extra>",
        )
    )
    return _apply_layout(
        fig,
        title="Cumulative Pipeline Backlog",
        xaxis_title="Date",
        yaxis_title="Cumulative Net Backlog (Children)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 6. Weekday Heatmap
# ─────────────────────────────────────────────────────────────────────────────
def plot_weekday_heatmap(weekday_df: pd.DataFrame) -> go.Figure:
    """Heatmap of average metrics by day of week.

    Parameters
    ----------
    weekday_df : DataFrame indexed (or columned) by ``day_of_week`` with
                 numeric columns for each metric.
    """
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Normalise structure
    if "day_of_week" in weekday_df.columns:
        wdf = weekday_df.set_index("day_of_week")
    else:
        wdf = weekday_df.copy()

    # Reindex to canonical day order (tolerate missing days)
    wdf = wdf.reindex([d for d in day_order if d in wdf.index])

    fig = go.Figure(
        go.Heatmap(
            z=wdf.values,
            x=wdf.columns.tolist(),
            y=wdf.index.tolist(),
            colorscale="YlOrRd",
            hovertemplate="Day: %{y}<br>Metric: %{x}<br>Avg: %{z:.1f}<extra></extra>",
        )
    )
    return _apply_layout(
        fig,
        title="Weekday Patterns: Average Daily Metrics",
        xaxis_title="Metric",
        yaxis_title="Day of Week",
        yaxis=dict(autorange="reversed"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# 7. Monthly Trends — Grouped Bar
# ─────────────────────────────────────────────────────────────────────────────
def plot_monthly_trends(monthly_df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart of monthly intake, transfers, and discharges.

    Parameters
    ----------
    monthly_df : DataFrame with a ``month`` (or ``year_month``) column
                 and ``cbp_apprehended``, ``cbp_transferred``,
                 ``hhs_discharged`` columns.
    """
    month_col = "month" if "month" in monthly_df.columns else "year_month"
    months = monthly_df[month_col].astype(str)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=months,
            y=monthly_df["cbp_apprehended"],
            name="Apprehensions",
            marker_color=COLOR_CBP,
            hovertemplate="Apprehensions: %{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=months,
            y=monthly_df["cbp_transferred"],
            name="Transfers",
            marker_color=COLOR_HHS,
            hovertemplate="Transfers: %{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=months,
            y=monthly_df["hhs_discharged"],
            name="Discharges",
            marker_color=COLOR_DISCHARGE,
            hovertemplate="Discharges: %{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(barmode="group")
    return _apply_layout(
        fig,
        title="Monthly Pipeline Flows",
        xaxis_title="Month",
        yaxis_title="Total Children",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 8. Discharge Stability — Rolling Mean ± Std + CV
# ─────────────────────────────────────────────────────────────────────────────
def plot_discharge_stability(variability_df: pd.DataFrame) -> go.Figure:
    """Discharge rolling mean ± 1-std band with CV overlay.

    Parameters
    ----------
    variability_df : DataFrame with columns ``date``,
                     ``discharge_rolling_mean``, ``discharge_rolling_std``,
                     ``discharge_cv``.
    """
    dates = variability_df["date"]
    mean = variability_df["discharge_rolling_mean"]
    std = variability_df["discharge_rolling_std"]
    cv = variability_df["discharge_cv"]

    upper = mean + std
    lower = (mean - std).clip(lower=0)

    fig = go.Figure()

    # Std band ----------------------------------------------------------------
    fig.add_trace(
        go.Scatter(
            x=pd.concat([dates, dates[::-1]], ignore_index=True),
            y=pd.concat([upper, lower[::-1]], ignore_index=True),
            fill="toself",
            fillcolor="rgba(44,160,44,0.15)",
            line=dict(width=0),
            showlegend=True,
            name="±1 Std Dev",
            hoverinfo="skip",
        )
    )

    # Rolling mean ------------------------------------------------------------
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=mean,
            name="Rolling Mean (Discharges)",
            mode="lines",
            line=dict(color=COLOR_DISCHARGE, width=2),
            hovertemplate="Mean: %{y:.1f}<extra></extra>",
        )
    )

    # CV on secondary axis ----------------------------------------------------
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=cv,
            name="Coefficient of Variation",
            mode="lines",
            line=dict(color=COLOR_ALERT, width=1.5, dash="dot"),
            yaxis="y2",
            hovertemplate="CV: %{y:.2f}<extra></extra>",
        )
    )

    return _apply_layout(
        fig,
        title="Discharge Stability: Rolling Mean & Variability",
        xaxis_title="Date",
        yaxis_title="Discharges",
        yaxis2=dict(
            title="CV",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# 9. KPI Gauge / Indicator
# ─────────────────────────────────────────────────────────────────────────────
def plot_kpi_gauge(
    value: float,
    title: str,
    thresholds: Dict[str, tuple],
) -> go.Figure:
    """Single KPI gauge.

    Parameters
    ----------
    value : Current KPI value.
    title : Display title.
    thresholds : ``{'good': (lo, hi), 'warning': (lo, hi),
                   'critical': (lo, hi)}``.
    """
    # Build step ranges for the gauge
    steps = []
    colors_map = {"good": "rgba(44,160,44,0.4)", "warning": "rgba(255,165,0,0.4)", "critical": "rgba(214,39,40,0.4)"}
    range_min = min(t[0] for t in thresholds.values())
    range_max = max(t[1] for t in thresholds.values())

    for level in ("good", "warning", "critical"):
        if level in thresholds:
            lo, hi = thresholds[level]
            steps.append(dict(range=[lo, hi], color=colors_map.get(level, COLOR_NEUTRAL)))

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title=dict(text=title, font=dict(size=16)),
            number=dict(font=dict(size=28), valueformat=".3f"),
            gauge=dict(
                axis=dict(range=[range_min, range_max]),
                bar=dict(color=COLOR_CBP),
                steps=steps,
                threshold=dict(
                    line=dict(color=COLOR_ALERT, width=3),
                    thickness=0.8,
                    value=value,
                ),
            ),
        )
    )
    return _apply_layout(fig, height=280)


# ─────────────────────────────────────────────────────────────────────────────
# 10. Outcome Trends — Monthly Discharges + MoM % Change
# ─────────────────────────────────────────────────────────────────────────────
def plot_outcome_trends(placement_df: pd.DataFrame) -> go.Figure:
    """Monthly discharge totals (bars) with MoM % change (line overlay).

    Parameters
    ----------
    placement_df : DataFrame with ``month`` (or ``year_month``),
                   ``hhs_discharged`` (monthly total), and
                   ``discharge_pct_change`` columns.
    """
    month_col = "month" if "month" in placement_df.columns else "year_month"
    months = placement_df[month_col].astype(str)

    fig = go.Figure()

    # Bars — monthly totals ---------------------------------------------------
    fig.add_trace(
        go.Bar(
            x=months,
            y=placement_df["hhs_discharged"],
            name="Monthly Discharges",
            marker_color=COLOR_DISCHARGE,
            hovertemplate="Discharges: %{y:,.0f}<extra></extra>",
        )
    )

    # Line — MoM % change on secondary y-axis ---------------------------------
    fig.add_trace(
        go.Scatter(
            x=months,
            y=placement_df["discharge_pct_change"],
            name="MoM % Change",
            mode="lines+markers",
            line=dict(color=COLOR_ALERT, width=2),
            marker=dict(size=5),
            yaxis="y2",
            hovertemplate="MoM Change: %{y:+.1f}%<extra></extra>",
        )
    )

    return _apply_layout(
        fig,
        title="Outcome Trends: Monthly Discharges & Change",
        xaxis_title="Month",
        yaxis_title="Total Discharges",
        yaxis2=dict(
            title="MoM % Change",
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=True,
            zerolinecolor=COLOR_NEUTRAL,
        ),
    )
