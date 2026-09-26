"""Tests for efficiency KPI calculations."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# Create test fixture for sample data
@pytest.fixture
def sample_data():
    """Create a 30-row test DataFrame with synthetic UAC data."""
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
def sample_data_with_zero():
    """Create test data with a zero denominator case."""
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')

    data = pd.DataFrame({
        'date': dates,
        'cbp_apprehended': np.random.randint(10, 51, 30),
        'cbp_custody': np.random.randint(30, 101, 30),
        'cbp_transferred': np.random.randint(5, 41, 30),
        'hhs_care': np.random.randint(2000, 3001, 30),
        'hhs_discharged': np.random.randint(5, 31, 30),
    })

    # Set one row to have zero CBP custody
    data.loc[10, 'cbp_custody'] = 0

    return data


@pytest.fixture
def empty_data():
    """Create an empty DataFrame for edge case testing."""
    return pd.DataFrame(columns=['date', 'cbp_apprehended', 'cbp_custody',
                                  'cbp_transferred', 'hhs_care', 'hhs_discharged'])


def test_transfer_efficiency_ratio(sample_data):
    """Verify transfer efficiency ratio equals cbp_transferred / cbp_custody for each row."""
    from src.analytics.efficiency import compute_all_kpis

    result = compute_all_kpis(sample_data)

    # Calculate expected values
    expected = sample_data['cbp_transferred'] / sample_data['cbp_custody']

    # Verify the transfer efficiency column matches expected
    pd.testing.assert_series_equal(
        result['transfer_efficiency'].dropna(),
        expected.dropna(),
        check_names=False,
        rtol=1e-5
    )


def test_discharge_effectiveness(sample_data):
    """Verify discharge effectiveness equals hhs_discharged / hhs_care for each row."""
    from src.analytics.efficiency import compute_all_kpis

    result = compute_all_kpis(sample_data)

    # Calculate expected values
    expected = sample_data['hhs_discharged'] / sample_data['hhs_care']

    # Verify the discharge effectiveness column matches expected
    pd.testing.assert_series_equal(
        result['discharge_effectiveness'].dropna(),
        expected.dropna(),
        check_names=False,
        rtol=1e-5
    )


def test_throughput_uses_rolling(sample_data):
    """Verify pipeline throughput uses rolling 7-day window."""
    from src.analytics.efficiency import compute_all_kpis

    result = compute_all_kpis(sample_data)

    # Verify throughput column exists
    assert 'pipeline_throughput' in result.columns

    # Calculate expected manually with 7-day rolling window
    # Throughput = rolling sum of exits / rolling sum of entries
    rolling_exits = sample_data['hhs_discharged'].rolling(window=7, min_periods=1).sum()
    rolling_entries = sample_data['cbp_apprehended'].rolling(window=7, min_periods=1).sum()
    expected = rolling_exits / rolling_entries

    pd.testing.assert_series_equal(
        result['pipeline_throughput'].dropna(),
        expected.dropna(),
        check_names=False,
        rtol=1e-5
    )


def test_zero_denominator_handling(sample_data_with_zero):
    """Verify no NaN/Inf in output when denominator is zero (should be 0 or handled)."""
    from src.analytics.efficiency import compute_all_kpis

    result = compute_all_kpis(sample_data_with_zero)

    # Check no inf values in transfer efficiency
    assert not np.isinf(result['transfer_efficiency']).any()

    # The row with zero custody should have NaN or 0 (handled gracefully)
    # Check that the function doesn't crash and returns valid numeric types
    assert result['transfer_efficiency'].dtype in [np.float64, np.float32]


def test_outcome_stability_bounds(sample_data):
    """Verify outcome stability score is bounded between 0 and 1."""
    from src.analytics.efficiency import compute_all_kpis

    result = compute_all_kpis(sample_data)

    # Verify outcome stability exists
    assert 'outcome_stability' in result.columns

    # Check bounds
    valid_scores = result['outcome_stability'].dropna()
    assert (valid_scores >= 0).all()
    assert (valid_scores <= 1).all()


def test_kpi_summary_keys(sample_data):
    """Verify compute_kpi_summary returns all 5 KPI names."""
    from src.analytics.efficiency import compute_kpi_summary

    summary = compute_kpi_summary(sample_data)

    expected_kpis = [
        'transfer_efficiency',
        'discharge_effectiveness',
        'pipeline_throughput',
        'backlog_accumulation',
        'outcome_stability'
    ]

    for kpi in expected_kpis:
        assert kpi in summary, f"Missing KPI: {kpi}"


def test_empty_dataframe(empty_data):
    """Verify functions handle empty DataFrame gracefully."""
    from src.analytics.efficiency import compute_all_kpis, compute_kpi_summary

    # Should not raise an error
    result = compute_all_kpis(empty_data)
    assert isinstance(result, pd.DataFrame)

    summary = compute_kpi_summary(empty_data)
    assert isinstance(summary, dict)
