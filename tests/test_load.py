"""Tests for data loading and validation."""

import pytest
import pandas as pd
from pathlib import Path


# Path to the actual data file
DATA_PATH = Path(__file__).parent.parent / 'data' / 'raw' / 'HHS_Unaccompanied_Alien_Children_Program.csv'


@pytest.fixture
def raw_csv_path():
    """Return path to the raw CSV file."""
    return DATA_PATH


def test_load_returns_dataframe(raw_csv_path):
    """Verify load_data() returns a DataFrame."""
    from src.data.load import load_data

    if raw_csv_path.exists():
        result = load_data(raw_csv_path)
        assert isinstance(result, pd.DataFrame)
    else:
        pytest.skip("Raw data file not found")


def test_column_names(raw_csv_path):
    """Verify renamed columns exist after loading."""
    from src.data.load import load_data

    if not raw_csv_path.exists():
        pytest.skip("Raw data file not found")

    result = load_data(raw_csv_path)

    expected_columns = [
        'date',
        'cbp_apprehended',
        'cbp_custody',
        'cbp_transferred',
        'hhs_care',
        'hhs_discharged'
    ]

    for col in expected_columns:
        assert col in result.columns, f"Missing expected column: {col}"


def test_no_empty_rows(raw_csv_path):
    """Verify no rows with all-null values."""
    from src.data.load import load_data

    if not raw_csv_path.exists():
        pytest.skip("Raw data file not found")

    result = load_data(raw_csv_path)

    # Check for completely empty rows
    empty_rows = result.isnull().all(axis=1).sum()
    assert empty_rows == 0, f"Found {empty_rows} completely empty rows"


def test_date_is_datetime(raw_csv_path):
    """Verify date column is datetime type."""
    from src.data.load import load_data

    if not raw_csv_path.exists():
        pytest.skip("Raw data file not found")

    result = load_data(raw_csv_path)

    assert pd.api.types.is_datetime64_any_dtype(result['date']), \
        f"Date column is {result['date'].dtype}, expected datetime"


def test_numeric_columns(raw_csv_path):
    """Verify numeric columns are numeric (not strings with commas)."""
    from src.data.load import load_data

    if not raw_csv_path.exists():
        pytest.skip("Raw data file not found")

    result = load_data(raw_csv_path)

    numeric_columns = [
        'cbp_apprehended',
        'cbp_custody',
        'cbp_transferred',
        'hhs_care',
        'hhs_discharged'
    ]

    for col in numeric_columns:
        assert pd.api.types.is_numeric_dtype(result[col]), \
            f"Column {col} is {result[col].dtype}, expected numeric"


def test_sorted_by_date(raw_csv_path):
    """Verify data is sorted ascending by date."""
    from src.data.load import load_data

    if not raw_csv_path.exists():
        pytest.skip("Raw data file not found")

    result = load_data(raw_csv_path)

    # Check that dates are in ascending order
    dates = result['date'].dropna()
    assert (dates.diff().dropna() >= pd.Timedelta(0)).all(), \
        "Data is not sorted in ascending order by date"
