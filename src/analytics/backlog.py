"""
Backlog & Delay Identification
==============================

Analyses focused on detecting when pipeline inflows exceed outflows for
sustained periods, causing children to accumulate in the system.

Key concepts
------------
- **Inflow**: children apprehended and placed in CBP custody
  (``cbp_apprehended``).
- **Outflow**: children discharged from HHS care to a sponsor
  (``hhs_discharged``).
- **Surplus / net inflow**: ``cbp_apprehended − hhs_discharged``.
  Positive means more children entered than exited the pipeline that
  day.
- **Backlog period**: a consecutive run of days where the surplus is
  positive (inflows exceed outflows continuously).
"""

import numpy as np
import pandas as pd


def compute_inflow_outflow(df: pd.DataFrame) -> pd.DataFrame:
    """Return daily inflow, outflow, and surplus.

    Columns returned
    ----------------
    date, inflow, outflow, surplus
    """
    return pd.DataFrame(
        {
            "date": df["date"],
            "inflow": df["cbp_apprehended"],
            "outflow": df["hhs_discharged"],
            "surplus": df["cbp_apprehended"] - df["hhs_discharged"],
        }
    ).reset_index(drop=True)


def compute_cumulative_backlog(df: pd.DataFrame) -> pd.DataFrame:
    """Cumulative sum of daily surplus (cbp_apprehended − hhs_discharged).

    A rising line means the total pipeline population is growing over
    time; a falling line means the system is clearing more than it
    receives.

    Returns
    -------
    pd.DataFrame
        Columns: date, daily_surplus, cumulative_backlog
    """
    surplus = df["cbp_apprehended"] - df["hhs_discharged"]
    return pd.DataFrame(
        {
            "date": df["date"],
            "daily_surplus": surplus,
            "cumulative_backlog": surplus.cumsum(),
        }
    ).reset_index(drop=True)


def detect_backlog_periods(
    df: pd.DataFrame,
    threshold_days: int = 7,
) -> pd.DataFrame:
    """Identify consecutive periods where daily surplus > 0.

    Only stretches lasting ``threshold_days`` or more are returned,
    since shorter blips are common noise.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain date, cbp_apprehended, hhs_discharged (sorted by
        date ascending).
    threshold_days : int, default 7
        Minimum consecutive days of positive surplus to qualify.

    Returns
    -------
    pd.DataFrame
        Columns: start_date, end_date, duration_days,
        total_surplus, avg_daily_surplus.
        Empty DataFrame (same columns) if no qualifying period is found.
    """
    surplus = (df["cbp_apprehended"] - df["hhs_discharged"]).values
    dates = df["date"].values

    # Identify groups of consecutive positive-surplus days
    positive = surplus > 0
    groups: list[dict] = []
    in_run = False
    start_idx = 0

    for i, val in enumerate(positive):
        if val and not in_run:
            in_run = True
            start_idx = i
        elif not val and in_run:
            in_run = False
            length = i - start_idx
            if length >= threshold_days:
                run_surplus = surplus[start_idx:i]
                groups.append(
                    {
                        "start_date": pd.Timestamp(dates[start_idx]),
                        "end_date": pd.Timestamp(dates[i - 1]),
                        "duration_days": length,
                        "total_surplus": int(run_surplus.sum()),
                        "avg_daily_surplus": round(float(run_surplus.mean()), 2),
                    }
                )

    # Handle a run that extends to the last row
    if in_run:
        length = len(positive) - start_idx
        if length >= threshold_days:
            run_surplus = surplus[start_idx:]
            groups.append(
                {
                    "start_date": pd.Timestamp(dates[start_idx]),
                    "end_date": pd.Timestamp(dates[-1]),
                    "duration_days": length,
                    "total_surplus": int(run_surplus.sum()),
                    "avg_daily_surplus": round(float(run_surplus.mean()), 2),
                }
            )

    columns = [
        "start_date",
        "end_date",
        "duration_days",
        "total_surplus",
        "avg_daily_surplus",
    ]
    if not groups:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(groups, columns=columns)
