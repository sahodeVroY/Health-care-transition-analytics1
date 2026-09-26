"""Data-quality validation for the UAC dataset.

Provides functions that inspect a cleaned DataFrame (output of
``src.data.load.load_data``) and return structured reports highlighting
potential quality issues.
"""

from typing import Any, Dict, List

import pandas as pd


def check_missing_values(df: pd.DataFrame) -> Dict[str, int]:
    """Return per-column counts of missing (NaN / NaT) values.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned UAC dataset.

    Returns
    -------
    dict
        ``{column_name: missing_count}`` for columns with ≥ 1 missing value.
    """
    counts = df.isna().sum()
    return {col: int(n) for col, n in counts.items() if n > 0}


def check_negative_values(df: pd.DataFrame) -> Dict[str, int]:
    """Return per-column counts of negative numeric values.

    All flow and stock fields should be non-negative.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned UAC dataset.

    Returns
    -------
    dict
        ``{column_name: negative_count}`` for columns with ≥ 1 negative value.
    """
    numeric_cols = df.select_dtypes(include="number").columns
    result: Dict[str, int] = {}
    for col in numeric_cols:
        neg_count = int((df[col] < 0).sum())
        if neg_count > 0:
            result[col] = neg_count
    return result


def check_date_gaps(df: pd.DataFrame, max_gap_days: int = 3) -> List[Dict[str, Any]]:
    """Identify gaps in the reporting timeline larger than *max_gap_days*.

    Because the source dataset does not report every calendar day (weekends
    and holidays are sometimes skipped), a gap threshold of 3 days is used
    by default so that normal weekend gaps are ignored.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a ``date`` column of type ``datetime64``.
    max_gap_days : int
        Minimum gap size (in days) to flag.  Defaults to 3.

    Returns
    -------
    list[dict]
        Each entry has keys ``from_date``, ``to_date``, ``gap_days``.
    """
    if "date" not in df.columns:
        raise KeyError("DataFrame must contain a 'date' column")

    sorted_dates = df["date"].sort_values().reset_index(drop=True)
    gaps: List[Dict[str, Any]] = []
    for i in range(1, len(sorted_dates)):
        delta = (sorted_dates[i] - sorted_dates[i - 1]).days
        if delta > max_gap_days:
            gaps.append(
                {
                    "from_date": sorted_dates[i - 1].strftime("%Y-%m-%d"),
                    "to_date": sorted_dates[i].strftime("%Y-%m-%d"),
                    "gap_days": delta,
                }
            )
    return gaps


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Division that returns *default* when the denominator is zero or NaN.

    Parameters
    ----------
    numerator : float
    denominator : float
    default : float
        Value to return on division-by-zero or NaN denominator.

    Returns
    -------
    float
    """
    if pd.isna(denominator) or denominator == 0:
        return default
    return numerator / denominator


def validate(df: pd.DataFrame) -> Dict[str, Any]:
    """Run all validation checks and compile a summary report.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned UAC dataset.

    Returns
    -------
    dict
        Keys:
        - ``row_count`` (int): number of rows
        - ``date_range`` (dict): ``{min, max}`` as ISO strings
        - ``missing_values`` (dict): per-column missing counts (may be empty)
        - ``negative_values`` (dict): per-column negative counts (may be empty)
        - ``date_gaps`` (list[dict]): gaps > 3 days
        - ``is_clean`` (bool): ``True`` when no issues were found
    """
    missing = check_missing_values(df)
    negatives = check_negative_values(df)
    gaps = check_date_gaps(df)

    date_range = {}
    if "date" in df.columns and not df["date"].isna().all():
        date_range = {
            "min": df["date"].min().strftime("%Y-%m-%d"),
            "max": df["date"].max().strftime("%Y-%m-%d"),
        }

    is_clean = len(missing) == 0 and len(negatives) == 0 and len(gaps) == 0

    return {
        "row_count": len(df),
        "date_range": date_range,
        "missing_values": missing,
        "negative_values": negatives,
        "date_gaps": gaps,
        "is_clean": is_clean,
    }
