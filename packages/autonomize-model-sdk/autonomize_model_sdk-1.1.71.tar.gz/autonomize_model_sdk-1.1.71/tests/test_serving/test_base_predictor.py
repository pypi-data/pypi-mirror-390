"""Tests for ModelHub base predictor classes."""

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from modelhub.serving.base import AutoModelPredictor


class TestModelHubPredictor:
    """Test base predictor class."""

    def test_init(self):
        """Test predictor initialization."""
        with patch("modelhub.serving.base.ModelhubCredential"):
            with patch("modelhub.serving.base.MLflowClient"):
                # Test with model URI
                predictor = AutoModelPredictor(
                    name="test-model", model_uri="runs:/abc123/model"
                )
                assert predictor.name == "test-model"
                assert predictor.model_uri == "runs:/abc123/model"
                assert predictor.model_name is None
                assert predictor.model_version is None
                assert not predictor.ready

                # Test with model name and version
                predictor = AutoModelPredictor(
                    name="test-model", model_name="my-model", model_version="2"
                )
                assert predictor.model_name == "my-model"
                assert predictor.model_version == "2"
                assert predictor.model_uri is None

    @patch("modelhub.serving.base.ModelhubCredential")
    @patch("modelhub.serving.base.MLflowClient")
    def test_load_with_uri(self, mock_client_class, mock_cred_class):
        """Test model loading with URI."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_model = MagicMock()
        mock_client.mlflow.pyfunc.load_model.return_value = mock_model

        mock_model_info = MagicMock()
        mock_model_info.signature = None
        mock_client.mlflow.models.get_model_info.return_value = mock_model_info

        # Create and load predictor
        predictor = AutoModelPredictor(
            name="test-model", model_uri="runs:/abc123/model"
        )

        assert predictor.load()
        assert predictor.ready
        assert predictor.model == mock_model

        # Verify correct URI was used
        mock_client.mlflow.pyfunc.load_model.assert_called_once_with(
            "runs:/abc123/model"
        )

    @patch("modelhub.serving.base.ModelhubCredential")
    @patch("modelhub.serving.base.MLflowClient")
    def test_load_with_model_name(self, mock_client_class, mock_cred_class):
        """Test model loading with model name."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_model = MagicMock()
        mock_client.mlflow.pyfunc.load_model.return_value = mock_model

        mock_model_info = MagicMock()
        mock_model_info.signature = None
        mock_client.mlflow.models.get_model_info.return_value = mock_model_info

        # Test with version
        predictor = AutoModelPredictor(
            name="test-model", model_name="my-model", model_version="3"
        )

        predictor.load()
        mock_client.mlflow.pyfunc.load_model.assert_called_with("models:/my-model/3")

        # Test without version (latest)
        predictor = AutoModelPredictor(name="test-model", model_name="my-model")

        predictor.load()
        mock_client.mlflow.pyfunc.load_model.assert_called_with(
            "models:/my-model/latest"
        )

    @patch("modelhub.serving.base.ModelhubCredential")
    @patch("modelhub.serving.base.MLflowClient")
    def test_health_check(self, mock_client_class, mock_cred_class):
        """Test health check."""
        predictor = AutoModelPredictor(
            name="test-model", model_uri="runs:/abc123/model"
        )

        # Before loading
        health = predictor.health_check()
        assert health["status"] == "loading"
        assert health["model_name"] == "test-model"

        # After loading
        predictor.ready = True
        health = predictor.health_check()
        assert health["status"] == "ready"


class TestAutoModelPredictor:
    """Test automatic model predictor."""

    @pytest.fixture
    def predictor(self):
        """Create a test predictor."""
        with patch("modelhub.serving.base.ModelhubCredential"):
            with patch("modelhub.serving.base.MLflowClient"):
                predictor = AutoModelPredictor(
                    name="test-model", model_uri="runs:/abc123/model"
                )
                predictor.model = MagicMock()
                predictor.ready = True
                return predictor

    def test_predict_not_ready(self, predictor):
        """Test prediction when model not ready."""
        predictor.ready = False
        result = predictor.predict({"text": "test"})
        assert result["status"] == 503
        assert "not loaded" in result["error"]

    def test_predict_v2_protocol(self, predictor):
        """Test V2 protocol prediction."""
        # Create V2 request
        request_data = {
            "model_name": "test-model",
            "inputs": [
                {
                    "name": "input",
                    "shape": [1, 3],
                    "datatype": "FP32",
                    "data": [1.0, 2.0, 3.0],
                }
            ],
        }

        # Mock model prediction
        predictor.model.predict.return_value = np.array([0.9])

        result = predictor.predict(request_data)

        assert "model_name" in result
        assert "outputs" in result
        assert len(result["outputs"]) == 1
        assert result["outputs"][0]["name"] == "output"

    def test_predict_legacy_text(self, predictor):
        """Test legacy text prediction."""
        predictor.model.predict.return_value = "positive"

        result = predictor.predict({"text": "This is great!"})

        assert result["status"] == 200
        assert result["data"]["prediction"] == "positive"
        # Model should have been called with DataFrame
        call_args = predictor.model.predict.call_args[0][0]
        assert isinstance(call_args, pd.DataFrame)

    def test_predict_legacy_tabular(self, predictor):
        """Test legacy tabular prediction."""
        # Test with list of records
        data = [{"feature1": 1, "feature2": 2}, {"feature1": 3, "feature2": 4}]

        predictor.model.predict.return_value = [0, 1]

        result = predictor.predict({"data": data})

        assert result["status"] == 200
        assert result["data"]["predictions"] == [0, 1]

        # Verify DataFrame was created
        call_args = predictor.model.predict.call_args[0][0]
        assert isinstance(call_args, pd.DataFrame)
        assert len(call_args) == 2

    def test_predict_legacy_image(self, predictor):
        """Test legacy image prediction."""
        image_data = b"fake-image-data"
        predictor.model.predict.return_value = {"class": "cat", "confidence": 0.95}

        result = predictor.predict({"image": image_data})

        assert result["status"] == 200
        assert result["data"]["class"] == "cat"

        # Verify DataFrame was created
        call_args = predictor.model.predict.call_args[0][0]
        assert isinstance(call_args, pd.DataFrame)
        assert "image" in call_args.columns
        assert call_args.at[0, "image"] == image_data

    def test_predict_legacy_pdf(self, predictor):
        """Test legacy PDF prediction."""
        pdf_data = b"fake-pdf-data"

        # Test with prediction_page_level column
        result_df = pd.DataFrame(
            {"prediction_page_level": ['{"page": 1, "text": "Hello"}']}
        )
        predictor.model.predict.return_value = result_df

        result = predictor.predict({"pdf_file": pdf_data})

        assert result["status"] == 200
        # JSON should be parsed
        assert result["data"]["prediction_page_level"]["page"] == 1
        assert result["data"]["prediction_page_level"]["text"] == "Hello"

        # Test with predictions column
        result_df = pd.DataFrame({"predictions": ['{"result": "success"}']})
        predictor.model.predict.return_value = result_df

        result = predictor.predict({"byte_stream": pdf_data})

        assert result["status"] == 200
        assert result["data"]["predictions"]["result"] == "success"

    def test_predict_bytes_input(self, predictor):
        """Test V2 protocol with bytes input."""
        request_data = {
            "inputs": [
                {
                    "name": "image",
                    "shape": [2],
                    "datatype": "BYTES",
                    "data": [b"image1", b"image2"],
                }
            ]
        }

        predictor.model.predict.return_value = [0.8, 0.2]

        predictor.predict(request_data)

        # Verify DataFrame was created with bytes
        call_args = predictor.model.predict.call_args[0][0]
        assert isinstance(call_args, pd.DataFrame)
        assert len(call_args) == 2
        assert call_args.at[0, "data"] == b"image1"
        assert call_args.at[1, "data"] == b"image2"

    def test_output_conversion(self, predictor):
        """Test different output format conversions."""
        # Test numpy array output
        predictor.model.predict.return_value = np.array([1, 2, 3])
        result = predictor.predict({"data": {"x": 1}})
        assert result["data"]["predictions"] == [1, 2, 3]

        # Test DataFrame output - multi-row returns dict with lists
        predictor.model.predict.return_value = pd.DataFrame(
            {"pred": [0.8, 0.2], "class": ["A", "B"]}
        )
        result = predictor.predict({"data": {"x": 1}})
        assert isinstance(result["data"], dict)
        assert result["data"]["pred"] == [0.8, 0.2]
        assert result["data"]["class"] == ["A", "B"]

        # Test Series output - wrapped in prediction key
        predictor.model.predict.return_value = pd.Series([1, 2, 3])
        result = predictor.predict({"data": {"x": 1}})
        assert isinstance(result["data"], dict)
        # Series is wrapped in "prediction" key
        assert "prediction" in result["data"]
        assert isinstance(result["data"]["prediction"], pd.Series)
        assert list(result["data"]["prediction"]) == [1, 2, 3]

    def test_error_handling(self, predictor):
        """Test error handling."""
        predictor.model.predict.side_effect = ValueError("Test error")

        result = predictor.predict({"text": "test"})

        assert result["status"] == 400
        assert "Test error" in result["error"]
