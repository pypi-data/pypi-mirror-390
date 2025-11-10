"""Tests for the LLMMonitor facade."""

from unittest.mock import ANY, MagicMock, mock_open, patch

import pandas as pd
import pytest

# Skip this entire module due to Evidently version compatibility issues
pytestmark = pytest.mark.skip(
    reason="Evidently ColumnMapping not available in current version"
)

try:
    from evidently import ColumnMapping
    from evidently.descriptors import Sentiment, TextLength, WordCount
    from evidently.report import Report
    from evidently.test_suite import TestSuite
except ImportError:
    ColumnMapping = None
    Sentiment = None
    TextLength = None
    WordCount = None
    Report = None
    TestSuite = None

from modelhub.monitors import LLMMonitor, MLMonitor


@pytest.fixture
def sample_llm_dataframe():
    """Create a sample DataFrame for LLM evaluations."""
    return pd.DataFrame(
        {
            "prompt": ["Explain AI in simple terms", "What is the capital of France?"],
            "response": [
                "AI is computer systems that can perform tasks that normally require human intelligence.",
                "The capital of France is Paris.",
            ],
            "reference_response": [
                "Artificial Intelligence refers to machines designed to think and learn like humans.",
                "Paris is the capital city of France.",
            ],
            "category": ["education", "geography"],
            "timestamp": pd.date_range(start="2023-01-01", periods=2),
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
def mock_ml_monitor():
    """Create a mock MLMonitor."""
    monitor = MagicMock(spec=MLMonitor)
    monitor.log_metrics_to_mlflow = MagicMock()
    monitor.save_and_log_report = MagicMock()
    return monitor


@pytest.fixture
def llm_monitor(mock_mlflow_client, mock_ml_monitor):
    """Create an LLMMonitor instance with mock dependencies."""
    return LLMMonitor(mlflow_client=mock_mlflow_client, ml_monitor=mock_ml_monitor)


def test_init_with_mlflow_client_only(mock_mlflow_client):
    """Test initialization with only an MLflow client."""
    # Patch the function that's directly imported in the LLMMonitor module
    with patch(
        "modelhub.monitors.llm_monitor.create_llm_monitor"
    ) as mock_create_llm_monitor:
        MagicMock()

        # Create the monitor
        monitor = LLMMonitor(mlflow_client=mock_mlflow_client)

        # Assertions
        assert monitor._monitor is not None
        mock_create_llm_monitor.assert_called_once()


def test_init_without_dependencies():
    """Test initialization without dependencies."""
    with patch(
        "modelhub.monitors.llm_monitor.create_llm_monitor"
    ) as mock_create_llm_monitor:
        LLMMonitor()

        mock_create_llm_monitor.assert_called_once()


def test_create_column_mapping(llm_monitor):
    """Test creating a column mapping for LLM data."""
    mapping = llm_monitor.create_column_mapping(
        datetime_col="timestamp",
        prompt_col="prompt",
        response_col="response",
        reference_col="reference_response",
        categorical_cols=["category"],
        datetime_cols=["created_at"],
        numerical_cols=["score"],
    )

    assert isinstance(mapping, ColumnMapping)
    assert mapping.datetime == "timestamp"
    assert mapping.text_features == ["prompt", "response", "reference_response"]
    assert mapping.categorical_features == ["category"]
    assert mapping.numerical_features == ["score"]
    assert mapping.datetime_features == ["created_at"]


def test_create_column_mapping_defaults(llm_monitor):
    """Test creating a column mapping with default values."""
    mapping = llm_monitor.create_column_mapping()

    assert isinstance(mapping, ColumnMapping)
    assert mapping.datetime is None
    assert mapping.text_features == ["prompt", "response"]
    assert len(mapping.categorical_features) == 0
    assert len(mapping.numerical_features) == 0
    assert len(mapping.datetime_features) == 0


@patch("modelhub.monitors.providers.evidently.evidently_llm_monitor.Report")
@patch("modelhub.monitors.providers.evidently.evidently_llm_monitor.TextEvals")
def test_evaluate_text_length(
    mock_text_evals, mock_report_class, llm_monitor, sample_llm_dataframe
):
    """Test evaluating text length metrics."""
    # Setup mocks
    mock_text_evals_instance = MagicMock()
    mock_text_evals.return_value = mock_text_evals_instance

    mock_report = MagicMock(spec=Report)
    mock_report_class.return_value = mock_report

    # Mock the provider's evaluate_text_length
    llm_monitor._monitor.evaluate_text_length = MagicMock(return_value=mock_report)

    # Call the method
    result = llm_monitor.evaluate_text_length(
        data=sample_llm_dataframe, response_col="response"
    )

    # Assertions
    assert result == mock_report
    llm_monitor._monitor.evaluate_text_length.assert_called_once_with(
        data=sample_llm_dataframe,
        response_col="response",
        reference_data=None,
        column_mapping=ANY,
        save_html=False,
        output_path="./reports",
    )


@patch("modelhub.monitors.providers.evidently.evidently_llm_monitor.Report")
@patch("modelhub.monitors.providers.evidently.evidently_llm_monitor.TextEvals")
def test_evaluate_text_length_with_saving(
    mock_text_evals, mock_report_class, llm_monitor, sample_llm_dataframe
):
    """Test evaluating text length metrics with saving enabled."""
    # Setup mocks
    mock_text_evals_instance = MagicMock()
    mock_text_evals.return_value = mock_text_evals_instance

    mock_report = MagicMock(spec=Report)
    mock_report_class.return_value = mock_report

    # Mock the provider's evaluate_text_length
    llm_monitor._monitor.evaluate_text_length = MagicMock(return_value=mock_report)

    # Call the method
    result = llm_monitor.evaluate_text_length(
        data=sample_llm_dataframe,
        response_col="response",
        save_html=True,
        output_path="/test/path",
    )

    # Assertions
    assert result == mock_report
    llm_monitor._monitor.evaluate_text_length.assert_called_once_with(
        data=sample_llm_dataframe,
        response_col="response",
        reference_data=None,
        column_mapping=ANY,
        save_html=True,
        output_path="/test/path",
    )


@patch("modelhub.monitors.providers.evidently.evidently_llm_monitor.Report")
@patch("modelhub.monitors.providers.evidently.evidently_llm_monitor.TextEvals")
@patch("modelhub.monitors.providers.evidently.evidently_llm_monitor.IncludesWords")
def test_evaluate_content_patterns(
    mock_includes_words,
    mock_text_evals,
    mock_report_class,
    llm_monitor,
    sample_llm_dataframe,
):
    """Test evaluating content patterns."""
    # Setup mocks
    mock_includes_words_instance = MagicMock()
    mock_includes_words.return_value = mock_includes_words_instance

    mock_text_evals_instance = MagicMock()
    mock_text_evals.return_value = mock_text_evals_instance

    mock_report = MagicMock(spec=Report)
    mock_report_class.return_value = mock_report

    # Mock the provider's evaluate_content_patterns
    llm_monitor._monitor.evaluate_content_patterns = MagicMock(return_value=mock_report)

    # Call the method
    result = llm_monitor.evaluate_content_patterns(
        data=sample_llm_dataframe,
        response_col="response",
        words_to_check=["AI", "capital"],
    )

    # Assertions
    assert result == mock_report
    llm_monitor._monitor.evaluate_content_patterns.assert_called_once_with(
        data=sample_llm_dataframe,
        response_col="response",
        words_to_check=["AI", "capital"],
        patterns_to_check=None,
        prefix_to_check=None,
        reference_data=None,
        column_mapping=ANY,
        save_html=False,
        output_path="./reports",
    )


@patch(
    "modelhub.monitors.providers.evidently.evidently_llm_monitor.LLM_JUDGE_AVAILABLE",
    False,
)
def test_evaluate_llm_as_judge_not_available(llm_monitor, sample_llm_dataframe):
    """Test evaluating LLM as judge when the feature is not available."""
    # Mock the provider's evaluate_llm_as_judge
    llm_monitor._monitor.evaluate_llm_as_judge = MagicMock(return_value=None)

    result = llm_monitor.evaluate_llm_as_judge(
        data=sample_llm_dataframe, response_col="response"
    )

    assert result is None
    llm_monitor._monitor.evaluate_llm_as_judge.assert_called_once()


@patch("modelhub.monitors.providers.evidently.evidently_llm_monitor.TestSuite")
def test_create_test_suite(mock_test_suite_class, llm_monitor):
    """Test creating a test suite."""
    # Setup mock
    mock_test_suite = MagicMock(spec=TestSuite)
    mock_test_suite_class.return_value = mock_test_suite

    # Mock the provider's create_test_suite
    llm_monitor._monitor.create_test_suite = MagicMock(return_value=mock_test_suite)

    # Call the method
    result = llm_monitor.create_test_suite(
        response_col="response",
        min_response_length=10,
        max_response_length=1000,
        min_sentiment=0.1,
        min_mean_response_length=50,
    )

    # Assertions
    assert result == mock_test_suite
    llm_monitor._monitor.create_test_suite.assert_called_once_with(
        response_col="response",
        min_response_length=10,
        max_response_length=1000,
        min_sentiment=0.1,
        min_mean_response_length=50,
    )


def test_run_comprehensive_evaluation(llm_monitor, sample_llm_dataframe):
    """Test running a comprehensive evaluation."""
    # Setup mocks
    mock_results = {
        "length_metrics": MagicMock(),
        "content_patterns": MagicMock(),
        "semantic_properties": MagicMock(),
        "llm_judge": MagicMock(),
        "test_suite": MagicMock(),
    }

    # Mock the provider's run_comprehensive_evaluation
    llm_monitor._monitor.run_comprehensive_evaluation = MagicMock(
        return_value=mock_results
    )

    # Call the method
    results = llm_monitor.run_comprehensive_evaluation(
        data=sample_llm_dataframe,
        response_col="response",
        prompt_col="prompt",
        reference_col="reference_response",
        categorical_cols=["category"],
        words_to_check=["AI", "capital"],
        run_sentiment=True,
        run_toxicity=True,
        run_llm_judge=True,
    )

    # Assertions
    assert results == mock_results
    llm_monitor._monitor.run_comprehensive_evaluation.assert_called_once()


def test_log_metrics_to_mlflow(llm_monitor, mock_ml_monitor):
    """Test logging metrics to MLflow."""
    # Setup mocks
    mock_report = MagicMock(spec=Report)

    # Make sure _monitor.log_metrics_to_mlflow is a proper MagicMock
    # Reset the mock to ensure it's properly configured
    llm_monitor._monitor.log_metrics_to_mlflow = MagicMock(return_value=True)

    # Call the method
    result = llm_monitor.log_metrics_to_mlflow(mock_report, run_id=None)

    # Assertions
    assert result is True
    llm_monitor._monitor.log_metrics_to_mlflow.assert_called_once_with(
        metrics=mock_report, run_id=None
    )


@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
def test_generate_summary_report(
    mock_file_open, mock_makedirs, llm_monitor, sample_llm_dataframe, mock_mlflow_client
):
    """Test generating a summary report."""
    # Add a sentiment column to the sample dataframe
    df = sample_llm_dataframe.copy()
    df["sentiment_score"] = [0.8, 0.3]

    # Mock the provider's generate_summary_report
    llm_monitor._monitor.generate_summary_report = MagicMock(
        return_value="/test/path/test_summary.html"
    )

    # Call the method
    result = llm_monitor.generate_summary_report(
        data=df,
        response_col="response",
        output_path="/test/path",
        report_name="test_summary.html",
        include_cols=["category", "sentiment_score"],
        artifact_path="llm_evaluation",
    )

    # Assertions
    assert result == "/test/path/test_summary.html"
    llm_monitor._monitor.generate_summary_report.assert_called_once_with(
        data=df,
        response_col="response",
        output_path="/test/path",
        report_name="test_summary.html",
        include_cols=["category", "sentiment_score"],
        artifact_path="llm_evaluation",
        run_id=None,
    )


def test_create_comparison_visualization(
    llm_monitor, sample_llm_dataframe, mock_mlflow_client
):
    """Test creating a comparison visualization."""
    # Create reference and current dataframes
    reference_data = sample_llm_dataframe.copy()
    current_data = sample_llm_dataframe.copy()

    # Mock the provider's create_comparison_visualization
    llm_monitor._monitor.create_comparison_visualization = MagicMock(
        return_value="./test/path/model_comparison_visualization.png"
    )

    # Call the method
    result = llm_monitor.create_comparison_visualization(
        reference_data=reference_data,
        current_data=current_data,
        output_path="./test/path",
        response_col="response",
        metrics=["length", "word_count"],
        artifact_path="llm_evaluation",
    )

    # Assertions
    assert result == "./test/path/model_comparison_visualization.png"
    llm_monitor._monitor.create_comparison_visualization.assert_called_once_with(
        reference_data=reference_data,
        current_data=current_data,
        output_path="./test/path",
        response_col="response",
        metrics=["length", "word_count"],
        artifact_path="llm_evaluation",
        run_id=None,
    )


def test_generate_comparison_report(
    llm_monitor, sample_llm_dataframe, mock_mlflow_client
):
    """Test generating a comparison report."""
    # Create reference and current dataframes
    reference_data = sample_llm_dataframe.copy()
    current_data = sample_llm_dataframe.copy()

    # Mock the provider's generate_comparison_report
    llm_monitor._monitor.generate_comparison_report = MagicMock(
        return_value="/test/path/test_comparison.html"
    )

    # Call the method
    result = llm_monitor.generate_comparison_report(
        reference_data=reference_data,
        current_data=current_data,
        response_col="response",
        category_col="category",
        metrics_cols=["sentiment_score"],
        output_path="/test/path",
        report_name="test_comparison.html",
        artifact_path="llm_evaluation",
    )

    # Assertions
    assert result == "/test/path/test_comparison.html"
    llm_monitor._monitor.generate_comparison_report.assert_called_once_with(
        reference_data=reference_data,
        current_data=current_data,
        response_col="response",
        category_col="category",
        metrics_cols=["sentiment_score"],
        output_path="/test/path",
        report_name="test_comparison.html",
        artifact_path="llm_evaluation",
        run_id=None,
    )


@patch("modelhub.monitors.providers.evidently.evidently_llm_monitor.os.makedirs")
def test_generate_dashboard(
    mock_makedirs, llm_monitor, sample_llm_dataframe, mock_mlflow_client
):
    """Test generating a dashboard visualization."""
    # Add columns to the dataframe
    df = sample_llm_dataframe.copy()
    df["sentiment_score"] = [0.8, 0.3]
    df["model"] = ["gpt-3.5", "gpt-4"]

    # Mock the provider's generate_dashboard
    llm_monitor._monitor.generate_dashboard = MagicMock(
        return_value="./test/path/dashboard.png"
    )

    # Call the method
    result = llm_monitor.generate_dashboard(
        data=df,
        response_col="response",
        category_col="category",
        model_col="model",
        sentiment_col="sentiment_score",
        output_path="./test/path",
        dashboard_name="dashboard.png",
        artifact_path="llm_evaluation",
    )

    # Assertions
    assert result == "./test/path/dashboard.png"
    llm_monitor._monitor.generate_dashboard.assert_called_once_with(
        data=df,
        response_col="response",
        category_col="category",
        model_col="model",
        sentiment_col="sentiment_score",
        output_path="./test/path",
        dashboard_name="dashboard.png",
        artifact_path="llm_evaluation",
        run_id=None,
    )
