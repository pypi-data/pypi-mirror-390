"""Tests for the MLMonitor facade."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

# Skip this entire module due to Evidently version compatibility issues
pytestmark = pytest.mark.skip(
    reason="Evidently ColumnMapping not available in current version"
)

try:
    from evidently import ColumnMapping
except ImportError:
    ColumnMapping = None

from modelhub.monitors import MLMonitor


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "num_feature": [1.0, 2.0, 3.0, 4.0, 5.0],
            "cat_feature": ["A", "B", "A", "C", "B"],
            "target": [0, 1, 0, 1, 1],
            "prediction": [0.1, 0.9, 0.2, 0.8, 0.7],
            "datetime_feature": pd.date_range(start="2023-01-01", periods=5),
        }
    )


@pytest.fixture
def mock_mlflow_client():
    """Create a mock MLflow client."""
    client = MagicMock()
    client.log_metric = MagicMock()
    client.log_artifact = MagicMock()
    client.mlflow = MagicMock()
    client.mlflow.log_metric = MagicMock()
    client.mlflow.log_artifact = MagicMock()
    return client


@pytest.fixture
def ml_monitor(mock_mlflow_client):
    """Create an MLMonitor instance with a mock MLflow client."""
    with patch("modelhub.monitors.factory.create_ml_monitor") as mock_create:
        # Create a mock monitor that will be returned by the factory
        mock_monitor = MagicMock()
        mock_create.return_value = mock_monitor

        monitor = MLMonitor(mlflow_client=mock_mlflow_client)
        # Directly expose the mock for testing
        monitor._monitor = mock_monitor
        return monitor


def test_create_column_mapping(ml_monitor):
    """Test creating a column mapping."""
    # Mock the implementation's create_column_mapping method
    ml_monitor._monitor.create_column_mapping = MagicMock(return_value=ColumnMapping())

    mapping = ml_monitor.create_column_mapping(
        target="target",
        prediction="prediction",
        numerical_features=["num_feature"],
        categorical_features=["cat_feature"],
        datetime_features=["datetime_feature"],
    )

    assert isinstance(mapping, ColumnMapping)
    ml_monitor._monitor.create_column_mapping.assert_called_once_with(
        target="target",
        prediction="prediction",
        numerical_features=["num_feature"],
        categorical_features=["cat_feature"],
        datetime_features=["datetime_feature"],
    )


def test_generate_report(ml_monitor, sample_dataframe):
    """Test generating a report."""
    # Setup mock return value
    mock_return = (MagicMock(), {"metric": "value"}, "/path/to/report.html")
    ml_monitor._monitor.generate_report = MagicMock(return_value=mock_return)

    # Call the method
    report, metrics, html_path = ml_monitor.generate_report(
        report_type="data_drift",
        reference_data=sample_dataframe,
        current_data=sample_dataframe,
        target_column="target",
        prediction_column="prediction",
        save_json=True,
        output_path="/test/path",
    )

    # Assertions
    assert report == mock_return[0]
    assert metrics == mock_return[1]
    assert html_path == mock_return[2]
    ml_monitor._monitor.generate_report.assert_called_once_with(
        report_type="data_drift",
        reference_data=sample_dataframe,
        current_data=sample_dataframe,
        target_column="target",
        prediction_column="prediction",
        column_mapping=None,
        column_name=None,
        save_json=True,
        output_path="/test/path",
        log_to_mlflow=False,
        artifact_path="reports",
        report_name=None,
        run_id=None,
    )


def test_run_and_log_reports(ml_monitor, sample_dataframe):
    """Test running and logging multiple reports."""
    # Setup mock return value
    mock_return = {
        "reports": {
            "data_drift": "/path/to/drift.html",
            "data_quality": "/path/to/quality.html",
        },
        "metrics": {
            "data_drift": {"drift_share": 0.2},
            "data_quality": {"quality_score": 0.95},
        },
    }
    ml_monitor._monitor.run_and_log_reports = MagicMock(return_value=mock_return)

    # Call the method
    results = ml_monitor.run_and_log_reports(
        reference_data=sample_dataframe,
        current_data=sample_dataframe,
        report_types=["data_drift", "data_quality"],
        target_column="target",
        prediction_column="prediction",
        report_prefix="test",
        output_path="/test/path",
        log_to_mlflow=True,
    )

    # Assertions
    assert results == mock_return
    ml_monitor._monitor.run_and_log_reports.assert_called_once_with(
        reference_data=sample_dataframe,
        current_data=sample_dataframe,
        report_types=["data_drift", "data_quality"],
        column_mapping=None,
        target_column="target",
        prediction_column="prediction",
        report_prefix="test",
        output_path="/test/path",
        log_to_mlflow=True,
        artifact_path="reports",
        run_id=None,
    )


def test_analyze_column_drift(ml_monitor, sample_dataframe):
    """Test analyzing drift for a specific column."""
    # Setup mock return value
    mock_return = ({"drift_detected": True, "drift_score": 0.8}, "/path/to/drift.html")
    ml_monitor._monitor.analyze_column_drift = MagicMock(return_value=mock_return)

    # Call the method
    metrics, html_path = ml_monitor.analyze_column_drift(
        reference_data=sample_dataframe,
        current_data=sample_dataframe,
        column_name="num_feature",
        save_json=True,
        output_path="/test/path",
        log_to_mlflow=True,
    )

    # Assertions
    assert metrics == mock_return[0]
    assert html_path == mock_return[1]
    ml_monitor._monitor.analyze_column_drift.assert_called_once_with(
        reference_data=sample_dataframe,
        current_data=sample_dataframe,
        column_name="num_feature",
        save_json=True,
        output_path="/test/path",
        log_to_mlflow=True,
        artifact_path="reports",
        report_prefix="",
        run_id=None,
    )


def test_log_metrics_to_mlflow(ml_monitor):
    """Test logging metrics to MLflow."""
    # Setup mock
    ml_monitor._monitor.log_metrics_to_mlflow = MagicMock(return_value=True)
    metrics = {"metric1": 1.0, "nested": {"metric2": 2.0}}

    # Call the method
    result = ml_monitor.log_metrics_to_mlflow(metrics)

    # Assertions
    assert result is True
    ml_monitor._monitor.log_metrics_to_mlflow.assert_called_once_with(
        metrics=metrics, run_id=None
    )


def test_log_metrics_to_mlflow_with_run_id(ml_monitor):
    """Test logging metrics to MLflow with a specific run ID."""
    # Setup mock
    ml_monitor._monitor.log_metrics_to_mlflow = MagicMock(return_value=True)
    metrics = {"metric1": 1.0}
    run_id = "test-run-id"

    # Call the method
    result = ml_monitor.log_metrics_to_mlflow(metrics, run_id=run_id)

    # Assertions
    assert result is True
    ml_monitor._monitor.log_metrics_to_mlflow.assert_called_once_with(
        metrics=metrics, run_id=run_id
    )


def test_save_and_log_report(ml_monitor):
    """Test saving and logging a report."""
    # Setup mock
    ml_monitor._monitor.save_and_log_report = MagicMock(
        return_value="/path/to/report.html"
    )
    mock_report = MagicMock()

    # Call the method
    result = ml_monitor.save_and_log_report(
        report=mock_report,
        report_name="test_report",
        output_path="/test/path",
        log_to_mlflow=True,
        artifact_path="test_artifacts",
    )

    # Assertions
    assert result == "/path/to/report.html"
    ml_monitor._monitor.save_and_log_report.assert_called_once_with(
        report=mock_report,
        report_name="test_report",
        output_path="/test/path",
        log_to_mlflow=True,
        artifact_path="test_artifacts",
        run_id=None,
    )
