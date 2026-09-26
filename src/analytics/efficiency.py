"""
Transition Efficiency Metrics
=============================

Derives the five required KPIs from the daily UAC dataset.

KPI Definitions
---------------

1. **Transfer Efficiency Ratio** (formula specified by requirements)
       Transfer Efficiency = cbp_transferred / cbp_custody
   Interpretation: fraction of children in CBP custody transferred to
   HHS on a given day.  Higher → faster CBP-to-HHS movement.

2. **Discharge Effectiveness** (formula specified by requirements)
       Discharge Effectiveness = hhs_discharged / hhs_care
   Interpretation: fraction of the HHS care population discharged
   (placed with a sponsor) on a given day.

3. **Pipeline Throughput Rate** (formula specified by requirements)
       Pipeline Throughput = Total Exits / Total Entries
   Operationalisation (documented here because the requirements ask us
   to state how Total Entries and Total Exits are derived):
       Total Exits  = 7-day rolling sum of hhs_discharged
       Total Entries = 7-day rolling sum of cbp_apprehended
   A 7-day rolling window smooths daily volatility while preserving
   weekly trends.  A value ≥ 1.0 means exits keep pace with entries.

4. **Backlog Accumulation Rate** (formula defined by this project)
       Backlog Accumulation Rate = rolling_7d_mean(
           cbp_apprehended − hhs_discharged)
   Interpretation: smoothed average daily net inflow.  Positive values
   indicate the pipeline population is growing (backlog building);
   negative values indicate drawdown.
   NOTE: This formula is NOT externally mandated.  It was designed for
   this project to capture sustained inflow/outflow imbalance.

5. **Outcome Stability Score** (formula defined by this project)
       Outcome Stability = 1 − CV_14d(hhs_discharged)
       where CV_14d = rolling_14d_std / rolling_14d_mean
   Clipped to [0, 1].
   Interpretation: measures consistency of discharge volumes.  A score
   near 1.0 means discharges are very stable; near 0.0 means highly
   variable or erratic.
   NOTE: This formula is NOT externally mandated.  It is a coefficient-
   of-variation-based measure chosen to capture placement reliability.

Division-by-zero handling
-------------------------
All ratios use ``np.where(denominator != 0, ratio, np.nan)`` so that
rows with a zero denominator produce NaN rather than inf or an error.
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Individual KPI helpers
# ---------------------------------------------------------------------------

def _transfer_efficiency(df: pd.DataFrame) -> pd.Series:
    """Transfer Efficiency Ratio = cbp_transferred / cbp_custody."""
    denom = df["cbp_custody"]
    return pd.Series(
        np.where(denom != 0, df["cbp_transferred"] / denom, np.nan),
        index=df.index,
        name="transfer_efficiency",
    )


def _discharge_effectiveness(df: pd.DataFrame) -> pd.Series:
    """Discharge Effectiveness = hhs_discharged / hhs_care."""
    denom = df["hhs_care"]
    return pd.Series(
        np.where(denom != 0, df["hhs_discharged"] / denom, np.nan),
        index=df.index,
        name="discharge_effectiveness",
    )


def _pipeline_throughput(df: pd.DataFrame) -> pd.Series:
    """Pipeline Throughput = rolling_7d_sum(discharges) / rolling_7d_sum(apprehensions)."""
    rolling_exits = df["hhs_discharged"].rolling(7, min_periods=1).sum()
    rolling_entries = df["cbp_apprehended"].rolling(7, min_periods=1).sum()
    return pd.Series(
        np.where(rolling_entries != 0, rolling_exits / rolling_entries, np.nan),
        index=df.index,
        name="pipeline_throughput",
    )


def _backlog_accumulation(df: pd.DataFrame) -> pd.Series:
    """Backlog Accumulation Rate = 7-day rolling mean of (apprehended − discharged)."""
    daily_net = df["cbp_apprehended"] - df["hhs_discharged"]
    return daily_net.rolling(7, min_periods=1).mean().rename("backlog_accumulation")


def _outcome_stability(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Outcome Stability Score = 1 − CV of discharges over *window* days.

    CV = rolling_std / rolling_mean.  Clipped to [0, 1].
    """
    rolling_mean = df["hhs_discharged"].rolling(window, min_periods=1).mean()
    rolling_std = df["hhs_discharged"].rolling(window, min_periods=1).std()
    cv = pd.Series(
        np.where(rolling_mean != 0, rolling_std / rolling_mean, np.nan),
        index=df.index,
    )
    score = (1 - cv).clip(0, 1)
    return score.rename("outcome_stability")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_all_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame with one row per reporting date and all 5 KPIs.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned daily data sorted by date ascending, containing:
        date, cbp_apprehended, cbp_custody, cbp_transferred,
        hhs_care, hhs_discharged.

    Returns
    -------
    pd.DataFrame
        Columns: date, transfer_efficiency, discharge_effectiveness,
        pipeline_throughput, backlog_accumulation, outcome_stability.
    """
    return pd.DataFrame(
        {
            "date": df["date"].values,
            "transfer_efficiency": _transfer_efficiency(df).values,
            "discharge_effectiveness": _discharge_effectiveness(df).values,
            "pipeline_throughput": _pipeline_throughput(df).values,
            "backlog_accumulation": _backlog_accumulation(df).values,
            "outcome_stability": _outcome_stability(df).values,
        }
    )


def compute_kpi_summary(df: pd.DataFrame) -> dict:
    """Compute period-level averages for each KPI.

    Returns
    -------
    dict
        Keys match the KPI column names; values are the mean over the
        period (NaN rows excluded).
    """
    kpis = compute_all_kpis(df)
    return {
        "transfer_efficiency": round(float(kpis["transfer_efficiency"].mean()), 4),
        "discharge_effectiveness": round(float(kpis["discharge_effectiveness"].mean()), 4),
        "pipeline_throughput": round(float(kpis["pipeline_throughput"].mean()), 4),
        "backlog_accumulation": round(float(kpis["backlog_accumulation"].mean()), 2),
        "outcome_stability": round(float(kpis["outcome_stability"].mean()), 4),
    }
