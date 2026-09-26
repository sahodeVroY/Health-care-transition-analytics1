"""Tests for backlog detection and analysis."""

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_data():
    """Create a test DataFrame with synthetic UAC data."""
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')

    return pd.DataFrame({
        'date': dates,
        'cbp_apprehended': np.random.randint(10, 51, 30),
        'cbp_custody': np.random.randint(30, 101, 30),
        'cbp_transferred': np.random.randint(5, 41, 30),
        'hhs_care': np.random.randint(2000, 3001, 30),
        'hhs_discharged': np.random.randint(5, 31, 30),
    })


@pytest.fixture
def sustained_surplus_data():
    """Create data with 10 consecutive days where inflow > outflow."""
    dates = pd.date_range(start='2024-01-01', periods=15, freq='D')

    return pd.DataFrame({
        'date': dates,
        'cbp_apprehended': [50, 55, 60, 58, 52, 48, 55, 60, 62, 58, 50, 45, 40, 35, 30],
        'cbp_custody': [100] * 15,
        'cbp_transferred': [40] * 15,
        'hhs_care': [2500] * 15,
        'hhs_discharged': [10, 8, 12, 9, 7, 11, 10, 8, 9, 7, 40, 50, 55, 60, 45],  # Low for first 10 days
    })


@pytest.fixture
def outflow_exceeds_data():
    """Create data where outflow > inflow (no backlog expected)."""
    dates = pd.date_range(start='2024-01-01', periods=15, freq='D')

    return pd.DataFrame({
        'date': dates,
        'cbp_apprehended': [10, 12, 15, 11, 13, 14, 12, 10, 11, 15, 12, 14, 13, 11, 12],
        'cbp_custody': [50] * 15,
        'cbp_transferred': [40] * 15,
        'hhs_care': [2500] * 15,
        'hhs_discharged': [30, 35, 40, 32, 38, 42, 35, 30, 33, 45, 40, 38, 42, 35, 38],  # High outflow
    })


def test_cumulative_backlog_shape(sample_data):
    """Verify output has expected columns."""
    from src.analytics.backlog import compute_cumulative_backlog

    result = compute_cumulative_backlog(sample_data)

    # Check expected columns exist
    expected_columns = ['daily_surplus', 'cumulative_backlog']
    for col in expected_columns:
        assert col in result.columns, f"Missing expected column: {col}"

    # Verify shape matches input
    assert len(result) == len(sample_data)


def test_inflow_outflow(sample_data):
    """Verify inflow = cbp_apprehended and outflow = hhs_discharged."""
    from src.analytics.backlog import compute_cumulative_backlog

    result = compute_cumulative_backlog(sample_data)

    # Daily surplus should be inflow - outflow
    expected_surplus = sample_data['cbp_apprehended'] - sample_data['hhs_discharged']

    pd.testing.assert_series_equal(
        result['daily_surplus'],
        expected_surplus,
        check_names=False
    )


def test_backlog_detection_with_sustained_surplus(sustained_surplus_data):
    """Verify detection of backlog when inflow exceeds outflow for sustained period."""
    from src.analytics.backlog import detect_backlog_periods

    # Detect backlog periods with threshold of 7 consecutive days
    backlog_periods = detect_backlog_periods(sustained_surplus_data, threshold_days=7)

    # Should detect at least one backlog period
    assert len(backlog_periods) > 0, "Expected to detect at least one backlog period"

    # The backlog period should start around day 0-2 (first few days of sustained surplus)
    first_period = backlog_periods.iloc[0]
    assert first_period['start_date'] <= sustained_surplus_data['date'].iloc[2]


def test_no_backlog_when_outflow_exceeds(outflow_exceeds_data):
    """Verify no backlog periods detected when outflow > inflow."""
    from src.analytics.backlog import detect_backlog_periods

    # Detect backlog periods
    backlog_periods = detect_backlog_periods(outflow_exceeds_data, threshold_days=5)

    # Should not detect any backlog periods
    assert len(backlog_periods) == 0, \
        f"Expected no backlog periods, but found {len(backlog_periods)}"
