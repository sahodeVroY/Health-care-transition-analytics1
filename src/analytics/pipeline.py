"""
Care Pipeline Modeling
======================

Represents the UAC care system as a multi-stage flow pipeline:

    CBP Custody → HHS Care → Sponsor Placement

**Flow variables** (daily counts that describe movement):
    - cbp_apprehended  – children entering CBP custody on a given day
    - cbp_transferred  – children moving from CBP to HHS on a given day
    - hhs_discharged   – children leaving HHS to a sponsor on a given day

**Stock variables** (point-in-time population counts):
    - cbp_custody – children currently held in CBP custody
    - hhs_care    – children currently in HHS care

Functions in this module compute pipeline-level summaries, daily flow /
stock tables, and net-flow series used downstream by backlog and
efficiency analytics.
"""

import numpy as np
import pandas as pd


def compute_pipeline_summary(df: pd.DataFrame) -> dict:
    """Return aggregate pipeline statistics over the full date range.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned daily data with columns:
        date, cbp_apprehended, cbp_custody, cbp_transferred,
        hhs_care, hhs_discharged.

    Returns
    -------
    dict
        Keys:
        - total_intake          – sum of cbp_apprehended
        - total_transfers       – sum of cbp_transferred
        - total_discharges      – sum of hhs_discharged
        - avg_cbp_custody       – mean of cbp_custody (stock)
        - avg_hhs_care          – mean of hhs_care (stock)
        - date_start / date_end – reporting-period boundaries
        - reporting_days        – number of rows
    """
    return {
        "total_intake": int(df["cbp_apprehended"].sum()),
        "total_transfers": int(df["cbp_transferred"].sum()),
        "total_discharges": int(df["hhs_discharged"].sum()),
        "avg_cbp_custody": round(float(df["cbp_custody"].mean()), 1),
        "avg_hhs_care": round(float(df["hhs_care"].mean()), 1),
        "date_start": df["date"].min(),
        "date_end": df["date"].max(),
        "reporting_days": len(df),
    }


def compute_daily_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Return a tidy daily table of flows and stocks.

    Columns returned
    ----------------
    date, intake, transfer, discharge   – flow variables
    cbp_custody, hhs_care               – stock variables
    """
    return pd.DataFrame(
        {
            "date": df["date"],
            "intake": df["cbp_apprehended"],
            "transfer": df["cbp_transferred"],
            "discharge": df["hhs_discharged"],
            "cbp_custody": df["cbp_custody"],
            "hhs_care": df["hhs_care"],
        }
    ).reset_index(drop=True)


def compute_net_flow(df: pd.DataFrame) -> pd.DataFrame:
    """Compute daily net flow through the entire pipeline.

    Definition
    ----------
    net_flow = cbp_apprehended − hhs_discharged

    A positive value means more children entered CBP than exited HHS on
    that day, implying the overall pipeline population grew.

    Returns
    -------
    pd.DataFrame
        Columns: date, cbp_apprehended, hhs_discharged, net_flow
    """
    net = df["cbp_apprehended"] - df["hhs_discharged"]
    return pd.DataFrame(
        {
            "date": df["date"],
            "cbp_apprehended": df["cbp_apprehended"],
            "hhs_discharged": df["hhs_discharged"],
            "net_flow": net,
        }
    ).reset_index(drop=True)
