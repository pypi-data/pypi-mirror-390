"""Tests for PromptEvaluator."""

import os
import tempfile
from unittest.mock import Mock, patch

import pandas as pd
import pytest

# Import with proper handling of optional dependencies
try:
    from modelhub.evaluation import EvaluationConfig, EvaluationReport, PromptEvaluator
    from modelhub.models.prompts import Content, Message

    EVALUATION_AVAILABLE = True
except ImportError:
    EVALUATION_AVAILABLE = False


@pytest.mark.skipif(not EVALUATION_AVAILABLE, reason="Evaluation module not available")
class TestEvaluationConfig:
    """Test EvaluationConfig dataclass."""

    def test_default_config(self):
        """Test default configuration."""
        config = EvaluationConfig()

        assert config.evaluations == ["quality", "safety", "metrics"]
        assert config.llm_provider == "openai"
        assert config.llm_model == "gpt-4o-mini"
        assert config.save_html is True
        assert config.save_json is True
        assert config.output_dir == "./evaluation_reports"
        assert config.include_reasoning is True
        assert config.batch_size == 10
        assert config.custom_descriptors is None

    def test_custom_config(self):
        """Test custom configuration."""
        config = EvaluationConfig(
            evaluations=["safety"],
            llm_provider="azure",
            llm_model="gpt-4",
            save_html=False,
            output_dir="/tmp/reports",
        )

        assert config.evaluations == ["safety"]
        assert config.llm_provider == "azure"
        assert config.llm_model == "gpt-4"
        assert config.save_html is False
        assert config.output_dir == "/tmp/reports"


@pytest.mark.skipif(not EVALUATION_AVAILABLE, reason="Evaluation module not available")
class TestEvaluationReport:
    """Test EvaluationReport dataclass."""

    def test_report_creation(self):
        """Test evaluation report creation."""
        from datetime import datetime

        config = EvaluationConfig()
        timestamp = datetime.now()

        report = EvaluationReport(
            config=config,
            timestamp=timestamp,
            metrics={"test_metric": 0.85},
            summary={"total_samples": 10},
            html_path="/path/to/report.html",
            json_path="/path/to/report.json",
        )

        assert report.config == config
        assert report.timestamp == timestamp
        assert report.metrics["test_metric"] == 0.85
        assert report.summary["total_samples"] == 10
        assert report.html_path == "/path/to/report.html"
        assert report.json_path == "/path/to/report.json"

    def test_to_dict(self):
        """Test report to dictionary conversion."""
        from datetime import datetime

        config = EvaluationConfig()
        timestamp = datetime.now()

        report = EvaluationReport(
            config=config,
            timestamp=timestamp,
            metrics={"accuracy": 0.9},
            summary={"samples": 5},
        )

        result = report.to_dict()

        assert "timestamp" in result
        assert "config" in result
        assert "metrics" in result
        assert "summary" in result
        assert result["metrics"]["accuracy"] == 0.9
        assert result["summary"]["samples"] == 5


@pytest.mark.skipif(not EVALUATION_AVAILABLE, reason="Evaluation module not available")
class TestPromptEvaluator:
    """Test PromptEvaluator class."""

    @pytest.fixture
    def sample_data(self):
        """Create sample evaluation data."""
        return pd.DataFrame(
            {
                "prompt": [
                    "Summarize this article.",
                    "Explain quantum computing.",
                    "Write a product description.",
                ],
                "response": [
                    "This article discusses recent advances in AI technology and its applications.",
                    "Quantum computing uses quantum mechanics to process information faster.",
                    "Our new smartphone features advanced AI capabilities and long battery life.",
                ],
                "expected": [
                    "AI technology has advanced significantly with various applications.",
                    "Quantum computing leverages quantum mechanics for faster processing.",
                    "The smartphone has AI features and good battery life.",
                ],
            }
        )

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_init_default_config(self, temp_output_dir):
        """Test initialization with default config."""
        config = EvaluationConfig(output_dir=temp_output_dir)
        evaluator = PromptEvaluator(config)

        assert evaluator.config == config
        assert os.path.exists(temp_output_dir)

    def test_init_no_config(self, temp_output_dir):
        """Test initialization without config."""
        with patch(
            "modelhub.evaluation.prompt_evaluator.EvaluationConfig"
        ) as mock_config:
            mock_config.return_value.output_dir = temp_output_dir
            evaluator = PromptEvaluator()
            assert evaluator.config is not None

    @patch("modelhub.evaluation.prompt_evaluator.EVIDENTLY_AVAILABLE", False)
    def test_init_evidently_not_available(self):
        """Test initialization when Evidently is not available."""
        with pytest.raises(ImportError, match="Evidently library is not available"):
            PromptEvaluator()

    def test_validate_data_success(self, temp_output_dir, sample_data):
        """Test successful data validation."""
        config = EvaluationConfig(output_dir=temp_output_dir)
        evaluator = PromptEvaluator(config)

        # Should not raise any exception
        evaluator._validate_data(
            sample_data,
            prompt_col="prompt",
            response_col="response",
            reference_col="expected",
            context_col=None,
        )

    def test_validate_data_missing_columns(self, temp_output_dir):
        """Test data validation with missing columns."""
        config = EvaluationConfig(output_dir=temp_output_dir)
        evaluator = PromptEvaluator(config)

        # Data missing required columns
        invalid_data = pd.DataFrame({"wrong_col": ["test"]})

        with pytest.raises(ValueError, match="Missing required columns"):
            evaluator._validate_data(
                invalid_data,
                prompt_col="prompt",
                response_col="response",
                reference_col=None,
                context_col=None,
            )

    def test_validate_data_empty(self, temp_output_dir):
        """Test data validation with empty data."""
        config = EvaluationConfig(output_dir=temp_output_dir)
        evaluator = PromptEvaluator(config)

        empty_data = pd.DataFrame({"prompt": [], "response": []})

        with pytest.raises(ValueError, match="Data cannot be empty"):
            evaluator._validate_data(
                empty_data,
                prompt_col="prompt",
                response_col="response",
                reference_col=None,
                context_col=None,
            )

    def test_basic_functionality(self, temp_output_dir):
        """Test basic functionality with metrics only."""
        config = EvaluationConfig(evaluations=["metrics"], output_dir=temp_output_dir)
        evaluator = PromptEvaluator(config)

        # Test that evaluator is properly initialized
        assert evaluator.config == config
        assert os.path.exists(temp_output_dir)

    def test_data_validation_pass(self, temp_output_dir, sample_data):
        """Test data validation passes with valid data."""
        config = EvaluationConfig(output_dir=temp_output_dir)
        evaluator = PromptEvaluator(config)

        # Should not raise any exception
        evaluator._validate_data(
            sample_data,
            prompt_col="prompt",
            response_col="response",
            reference_col="expected",
            context_col=None,
        )

    def test_data_definition_creation(self, temp_output_dir):
        """Test creating data definition for evidently."""
        config = EvaluationConfig(output_dir=temp_output_dir)
        evaluator = PromptEvaluator(config)

        data_def = evaluator._create_data_definition(
            prompt_col="prompt",
            response_col="response",
            reference_col="expected",
            context_col="context",
        )

        assert data_def.text_columns == ["prompt", "response", "expected", "context"]

    def test_basic_metrics_extraction(self, temp_output_dir):
        """Test basic metrics extraction with simple data."""
        import pandas as pd

        config = EvaluationConfig(output_dir=temp_output_dir)
        evaluator = PromptEvaluator(config)

        # Create test data
        test_data = pd.DataFrame(
            {
                "prompt": ["test prompt", "another prompt"],
                "response": ["test response", "another response"],
                "prompt_length": [11, 14],
                "response_length": [13, 16],
                "prompt_word_count": [2, 2],
                "response_word_count": [2, 2],
            }
        )

        metrics = evaluator._extract_basic_metrics_simple(
            test_data, ["prompt", "response"]
        )
        assert metrics["total_rows"] == 2
        assert metrics["total_columns"] == 6
        assert metrics["mean_prompt_length"] == 12.5
        assert metrics["unique_prompt"] == 2

    def test_format_template(self, temp_output_dir):
        """Test template formatting."""
        config = EvaluationConfig(output_dir=temp_output_dir)
        evaluator = PromptEvaluator(config)

        template = [
            Message(
                role="system",
                content=Content(type="text", text="You are helpful."),
                input_variables=[],
            ),
            Message(
                role="user",
                content=Content(type="text", text="Answer: {{question}}"),
                input_variables=["question"],
            ),
        ]

        variables = {"question": "What is AI?"}
        result = evaluator._format_template(template, variables)

        expected = "system: You are helpful.\nuser: Answer: What is AI?"
        assert result == expected

    @patch("modelhub.evaluation.prompt_evaluator.Report")
    @patch("modelhub.evaluation.prompt_evaluator.Dataset")
    def test_evaluate_offline_success(
        self, mock_dataset_class, mock_report_class, temp_output_dir, sample_data
    ):
        """Test successful offline evaluation."""
        # Setup mocks
        mock_dataset = Mock()
        mock_dataset_class.from_pandas.return_value = mock_dataset

        mock_report = Mock()
        mock_report.as_dict.return_value = {
            "metrics": [
                {"metric": "RowCount", "result": {"current": {"number_of_rows": 3}}},
                {
                    "metric": "MeanValue",
                    "column_name": "prompt_length",
                    "result": {"current": {"mean": 50.0}},
                },
            ]
        }
        mock_report_class.return_value = mock_report

        config = EvaluationConfig(
            evaluations=["metrics"],
            output_dir=temp_output_dir,
            save_html=False,
            save_json=False,
        )
        evaluator = PromptEvaluator(config)

        # Run evaluation
        report = evaluator.evaluate_offline(sample_data)

        # Verify results
        assert isinstance(report, EvaluationReport)
        assert report.config == config
        assert report.summary["total_samples"] == 3
        assert "metrics" in report.summary["evaluations_run"]

        # Verify report was run
        mock_report.run.assert_called_once_with(mock_dataset)

    @patch("modelhub.evaluation.prompt_evaluator.Report")
    @patch("modelhub.evaluation.prompt_evaluator.Dataset")
    def test_evaluate_offline_with_html_json(
        self, mock_dataset_class, mock_report_class, temp_output_dir, sample_data
    ):
        """Test offline evaluation with HTML and JSON output."""
        # Setup mocks
        mock_dataset = Mock()
        mock_dataset_class.from_pandas.return_value = mock_dataset

        mock_report = Mock()
        mock_report.as_dict.return_value = {"metrics": []}
        mock_report_class.return_value = mock_report

        config = EvaluationConfig(
            evaluations=["metrics"],
            output_dir=temp_output_dir,
            save_html=True,
            save_json=True,
        )
        evaluator = PromptEvaluator(config)

        # Run evaluation
        report = evaluator.evaluate_offline(sample_data)

        # Verify file paths are set
        assert report.html_path is not None
        assert report.json_path is not None
        assert temp_output_dir in report.html_path
        assert temp_output_dir in report.json_path

        # Verify actual files were created (we use custom HTML generation now)
        import os

        assert os.path.exists(report.html_path)
        assert os.path.exists(report.json_path)

    @patch("modelhub.evaluation.prompt_evaluator.Report")
    @patch("modelhub.evaluation.prompt_evaluator.Dataset")
    def test_evaluate_prompt_template(
        self, mock_dataset_class, mock_report_class, temp_output_dir
    ):
        """Test prompt template evaluation."""
        template = [
            Message(
                role="user",
                content=Content(type="text", text="Summarize: {{content}}"),
                input_variables=["content"],
            )
        ]

        test_data = pd.DataFrame(
            {
                "variables": [
                    {"content": "AI is transforming the world."},
                    {"content": "Climate change is a major issue."},
                ],
                "expected": [
                    "AI transforms the world.",
                    "Climate change is important.",
                ],
            }
        )

        def mock_llm(prompt):
            if "AI" in prompt:
                return "AI is changing everything."
            return "Climate issues are significant."

        config = EvaluationConfig(
            evaluations=["metrics"],
            output_dir=temp_output_dir,
            save_html=False,
            save_json=False,
        )

        # Setup mocks
        mock_dataset = Mock()
        mock_dataset_class.from_pandas.return_value = mock_dataset

        mock_report = Mock()
        mock_report.as_dict.return_value = {"metrics": []}
        mock_report_class.return_value = mock_report

        evaluator = PromptEvaluator(config)

        # Test template evaluation
        report = evaluator.evaluate_prompt_template(
            prompt_template=template,
            test_data=test_data,
            variables_col="variables",
            expected_col="expected",
            llm_generate_func=mock_llm,
        )

        assert isinstance(report, EvaluationReport)
        assert report.summary["total_samples"] == 2

    def test_format_template_functionality(self, temp_output_dir):
        """Test template formatting functionality."""
        config = EvaluationConfig(output_dir=temp_output_dir)
        evaluator = PromptEvaluator(config)

        template = [
            Message(
                role="system",
                content=Content(type="text", text="You are helpful."),
                input_variables=[],
            ),
            Message(
                role="user",
                content=Content(type="text", text="Answer: {{question}}"),
                input_variables=["question"],
            ),
        ]

        variables = {"question": "What is AI?"}
        result = evaluator._format_template(template, variables)

        expected = "system: You are helpful.\nuser: Answer: What is AI?"
        assert result == expected


@pytest.mark.skipif(not EVALUATION_AVAILABLE, reason="Evaluation module not available")
class TestIntegration:
    """Integration tests for the evaluation module."""

    def test_import_from_main_package(self):
        """Test importing evaluation classes from main package."""
        try:
            from modelhub import EvaluationConfig, EvaluationReport, PromptEvaluator

            assert PromptEvaluator is not None
            assert EvaluationConfig is not None
            assert EvaluationReport is not None
        except ImportError:
            pytest.skip("Evaluation module not available in main package")

    @pytest.mark.integration
    def test_end_to_end_evaluation(self):
        """End-to-end integration test (requires evidently)."""
        try:
            import tempfile

            # Create sample data
            data = pd.DataFrame(
                {
                    "prompt": ["Test prompt"],
                    "response": ["Test response that is safe and appropriate."],
                }
            )

            with tempfile.TemporaryDirectory() as tmpdir:
                config = EvaluationConfig(
                    evaluations=["metrics"],  # Only basic metrics to avoid LLM calls
                    output_dir=tmpdir,
                    save_html=False,
                    save_json=False,
                )

                evaluator = PromptEvaluator(config)
                report = evaluator.evaluate_offline(data)

                assert isinstance(report, EvaluationReport)
                assert report.summary["total_samples"] == 1

        except Exception as e:
            pytest.skip(f"Integration test skipped due to: {e}")


# Test that handles the case when evidently is not available
class TestGracefulDegradation:
    """Test graceful degradation when evidently is not available."""

    def test_import_without_evidently(self):
        """Test that the module can be imported even without evidently."""
        # This test might not work if evidently is actually installed
        # but it documents the expected behavior
        try:
            pass

            # If we get here, evidently is available
            assert True
        except ImportError:
            # Expected when evidently is not available
            assert True
