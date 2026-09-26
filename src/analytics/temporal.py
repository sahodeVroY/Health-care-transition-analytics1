"""
Temporal & Pattern Analysis
===========================

Evaluates time-based patterns in pipeline flows and efficiency:
- Weekday versus weekend differences
- Monthly aggregates and trends
- Detection of periods where pipeline movement stagnates
"""

import numpy as np
import pandas as pd


def weekday_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Compute average metrics grouped by day-of-week.

    Returns
    -------
    pd.DataFrame
        Index: day_of_week (0=Monday, ..., 6=Sunday)
        Columns: avg_apprehended, avg_transferred, avg_discharged,
                 avg_cbp_custody, avg_hhs_care
    """
    df = df.copy()
    df["day_of_week"] = pd.to_datetime(df["date"]).dt.dayofweek

    agg = df.groupby("day_of_week").agg(
        {
            "cbp_apprehended": "mean",
            "cbp_transferred": "mean",
            "hhs_discharged": "mean",
            "cbp_custody": "mean",
            "hhs_care": "mean",
        }
    )

    agg.columns = [
        "avg_apprehended",
        "avg_transferred",
        "avg_discharged",
        "avg_cbp_custody",
        "avg_hhs_care",
    ]

    # Add day name for readability
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    agg["day_name"] = [day_names[i] for i in agg.index]

    return agg.reset_index()


def monthly_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate metrics by month.

    Returns
    -------
    pd.DataFrame
        Columns: year, month, total_apprehended, total_transferred,
                 total_discharged, avg_cbp_custody, avg_hhs_care
    """
    df = df.copy()
    df["year_month"] = pd.to_datetime(df["date"]).dt.to_period("M")

    agg = df.groupby("year_month").agg(
        {
            "cbp_apprehended": "sum",
            "cbp_transferred": "sum",
            "hhs_discharged": "sum",
            "cbp_custody": "mean",
            "hhs_care": "mean",
        }
    )

    agg.columns = [
        "total_apprehended",
        "total_transferred",
        "total_discharged",
        "avg_cbp_custody",
        "avg_hhs_care",
    ]

    result = agg.reset_index()
    result["year"] = result["year_month"].dt.year
    result["month"] = result["year_month"].dt.month
    result = result.drop(columns=["year_month"])

    return result[
        [
            "year",
            "month",
            "total_apprehended",
            "total_transferred",
            "total_discharged",
            "avg_cbp_custody",
            "avg_hhs_care",
        ]
    ]


def detect_stagnation(
    df: pd.DataFrame,
    window: int = 14,
    threshold: float = 0.02,
) -> pd.DataFrame:
    """Detect periods where pipeline throughput is flat.

    Stagnation is defined as consecutive days where the rolling standard
    deviation of the throughput ratio falls below ``threshold``.

    Parameters
    ----------
    df : pd.DataFrame
        Daily data with cbp_apprehended and hhs_discharged.
    window : int, default 14
        Rolling window size for computing throughput and its std dev.
    threshold : float, default 0.02
        Max std dev to qualify as stagnant.

    Returns
    -------
    pd.DataFrame
        Columns: start_date, end_date, duration_days, avg_throughput.
        Empty if no stagnation periods found.
    """
    # Compute daily throughput ratio (protecting against zero denominator)
    denom = df["cbp_apprehended"]
    throughput = pd.Series(
        np.where(denom != 0, df["hhs_discharged"] / denom, np.nan),
        index=df.index,
    )

    # Rolling std of throughput
    rolling_std = throughput.rolling(window, min_periods=window // 2).std()

    # Mark days where std is below threshold
    stagnant = rolling_std < threshold
    dates = df["date"].values

    # Identify consecutive runs
    groups: list[dict] = []
    in_run = False
    start_idx = 0

    for i, val in enumerate(stagnant):
        if val and not in_run:
            in_run = True
            start_idx = i
        elif not val and in_run:
            in_run = False
            run_throughput = throughput.iloc[start_idx:i]
            groups.append(
                {
                    "start_date": pd.Timestamp(dates[start_idx]),
                    "end_date": pd.Timestamp(dates[i - 1]),
                    "duration_days": i - start_idx,
                    "avg_throughput": round(float(run_throughput.mean()), 4),
                }
            )

    # Handle run extending to the end
    if in_run:
        run_throughput = throughput.iloc[start_idx:]
        groups.append(
            {
                "start_date": pd.Timestamp(dates[start_idx]),
                "end_date": pd.Timestamp(dates[-1]),
                "duration_days": len(dates) - start_idx,
                "avg_throughput": round(float(run_throughput.mean()), 4),
            }
        )

    columns = ["start_date", "end_date", "duration_days", "avg_throughput"]
    if not groups:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(groups, columns=columns)
