"""
Outcome Stability Analysis
==========================

Evaluates the variability, trends, and sudden changes in discharge
volumes and placement outcomes.

Reliable reunification systems produce consistent discharge volumes;
sudden drops or high variability may indicate operational or systemic
problems.
"""

import numpy as np
import pandas as pd


def discharge_variability(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Compute rolling statistics on discharge volumes.

    Parameters
    ----------
    df : pd.DataFrame
        Daily data with columns date and hhs_discharged.
    window : int, default 14
        Rolling window size.

    Returns
    -------
    pd.DataFrame
        Columns: date, hhs_discharged, rolling_mean, rolling_std,
                 coefficient_of_variation.
    """
    discharged = df["hhs_discharged"]
    rolling_mean = discharged.rolling(window, min_periods=1).mean()
    rolling_std = discharged.rolling(window, min_periods=1).std()

    cv = pd.Series(
        np.where(rolling_mean != 0, rolling_std / rolling_mean, np.nan),
        index=df.index,
    )

    return pd.DataFrame(
        {
            "date": df["date"],
            "hhs_discharged": discharged,
            "rolling_mean": rolling_mean,
            "rolling_std": rolling_std,
            "coefficient_of_variation": cv,
        }
    ).reset_index(drop=True)


def placement_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Compute monthly discharge totals and month-over-month change.

    Returns
    -------
    pd.DataFrame
        Columns: year, month, total_discharged, mom_change, mom_pct_change.
    """
    df = df.copy()
    df["year_month"] = pd.to_datetime(df["date"]).dt.to_period("M")

    monthly = (
        df.groupby("year_month")
        .agg({"hhs_discharged": "sum"})
        .rename(columns={"hhs_discharged": "total_discharged"})
    )

    monthly["mom_change"] = monthly["total_discharged"].diff()

    prev = monthly["total_discharged"].shift(1)
    monthly["mom_pct_change"] = np.where(
        prev != 0,
        (monthly["total_discharged"] - prev) / prev * 100,
        np.nan,
    )

    result = monthly.reset_index()
    result["year"] = result["year_month"].dt.year
    result["month"] = result["year_month"].dt.month
    result = result.drop(columns=["year_month"])

    return result[["year", "month", "total_discharged", "mom_change", "mom_pct_change"]]


def detect_sudden_drops(
    df: pd.DataFrame,
    pct_threshold: float = -0.3,
) -> pd.DataFrame:
    """Identify days where discharge volume dropped significantly.

    A "sudden drop" is defined as a day where hhs_discharged fell by
    more than ``pct_threshold`` (expressed as a decimal) compared to
    the 7-day rolling average of the preceding period.

    Parameters
    ----------
    df : pd.DataFrame
        Daily data with date and hhs_discharged.
    pct_threshold : float, default -0.3
        Minimum percentage drop to flag (e.g., -0.3 = 30% decline).

    Returns
    -------
    pd.DataFrame
        Columns: date, hhs_discharged, baseline_avg, pct_drop.
        Rows are dates where the drop exceeds the threshold.
    """
    discharged = df["hhs_discharged"].values
    dates = df["date"].values

    # Compute 7-day rolling average (shifted by 1 so we compare to the
    # *prior* week, not including today)
    baseline = (
        pd.Series(discharged)
        .shift(1)
        .rolling(7, min_periods=1)
        .mean()
        .values
    )

    pct_change = np.where(
        baseline != 0,
        (discharged - baseline) / baseline,
        np.nan,
    )

    # Filter to rows where pct_change < pct_threshold
    mask = pct_change < pct_threshold

    drops = pd.DataFrame(
        {
            "date": dates[mask],
            "hhs_discharged": discharged[mask],
            "baseline_avg": baseline[mask],
            "pct_drop": pct_change[mask] * 100,  # convert to percentage
        }
    )

    return drops.reset_index(drop=True)
