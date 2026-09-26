"""Data loading utilities for the UAC Care-Transition Analytics project.

Loads the HHS Unaccompanied Alien Children Program CSV, cleans it, and
returns a tidy DataFrame ready for downstream analytics.
"""

from pathlib import Path
from typing import Optional

import pandas as pd

# ── Column name mapping ─────────────────────────────────────────────
_RAW_TO_CLEAN = {
    "Date": "date",
    "Children apprehended and placed in CBP custody*": "cbp_apprehended",
    "Children in CBP custody": "cbp_custody",
    "Children transferred out of CBP custody": "cbp_transferred",
    "Children in HHS Care": "hhs_care",
    "Children discharged from HHS Care": "hhs_discharged",
}

_NUMERIC_COLS = [
    "cbp_apprehended",
    "cbp_custody",
    "cbp_transferred",
    "hhs_care",
    "hhs_discharged",
]

# Default path relative to the project root
_DEFAULT_CSV = Path(__file__).resolve().parents[2] / "data" / "raw" / "HHS_Unaccompanied_Alien_Children_Program.csv"


def load_raw(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """Load the raw CSV exactly as-is (no cleaning).

    Parameters
    ----------
    csv_path : Path, optional
        Path to the CSV file.  Defaults to ``data/raw/...csv`` inside the
        project tree.

    Returns
    -------
    pd.DataFrame
    """
    path = Path(csv_path) if csv_path else _DEFAULT_CSV
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}")
    return pd.read_csv(path)


def load_data(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """Load, clean, and return the UAC dataset.

    Steps
    -----
    1. Read CSV.
    2. Rename columns to short snake_case names.
    3. Drop rows where every field is empty (trailing blank rows).
    4. Strip commas from numeric strings and cast to ``int`` / ``float``.
    5. Parse the *date* column into ``datetime``.
    6. Sort ascending by date.
    7. Reset index.

    Parameters
    ----------
    csv_path : Path, optional
        Override the default CSV location.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with columns:
        ``date | cbp_apprehended | cbp_custody | cbp_transferred |
        hhs_care | hhs_discharged``
    """
    df = load_raw(csv_path)

    # ── Rename ──────────────────────────────────────────────────────
    df = df.rename(columns=_RAW_TO_CLEAN)

    # ── Drop fully-empty rows ───────────────────────────────────────
    df = df.dropna(subset=["date"], how="any")
    df = df[df["date"].astype(str).str.strip() != ""]

    # ── Clean numeric columns (remove commas, coerce to numeric) ────
    for col in _NUMERIC_COLS:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── Parse dates ─────────────────────────────────────────────────
    df["date"] = pd.to_datetime(df["date"], format="%B %d, %Y", errors="coerce")

    # Drop any rows where the date could not be parsed
    df = df.dropna(subset=["date"])

    # ── Sort and reset ──────────────────────────────────────────────
    df = df.sort_values("date").reset_index(drop=True)

    return df


def save_processed(df: pd.DataFrame, out_path: Optional[Path] = None) -> Path:
    """Persist a cleaned DataFrame to ``data/processed/``.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned data (output of :func:`load_data`).
    out_path : Path, optional
        Destination file.  Defaults to
        ``data/processed/uac_cleaned.csv``.

    Returns
    -------
    Path
        The path the file was written to.
    """
    dest = Path(out_path) if out_path else (
        Path(__file__).resolve().parents[2] / "data" / "processed" / "uac_cleaned.csv"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dest, index=False)
    return dest
