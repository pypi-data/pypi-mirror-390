"""
Enhanced tests for AutoModelPredictor with inference type detection.
"""

import json
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest

from modelhub.serving.base import AutoModelPredictor
from modelhub.serving.inference_types import InferenceType


class TestAutoModelPredictorEnhanced:
    """Test enhanced AutoModelPredictor with inference types."""

    @pytest.fixture
    def predictor(self):
        """Create a test predictor with mocked dependencies."""
        with patch("modelhub.serving.base.ModelhubCredential"):
            with patch("modelhub.serving.base.MLflowClient"):
                predictor = AutoModelPredictor(
                    name="test-model", model_uri="runs:/abc123/model"
                )
                predictor.model = MagicMock()
                predictor.ready = True
                predictor.model_metadata = MagicMock()
                predictor.model_metadata.outputs = [
                    {"name": "predictions"},
                    {"name": "confidence"},
                ]
                return predictor

    def test_init_with_inference_type_override(self):
        """Test initialization with inference type override."""
        with patch("modelhub.serving.base.ModelhubCredential"):
            with patch("modelhub.serving.base.MLflowClient"):
                predictor = AutoModelPredictor(
                    name="test-model",
                    model_uri="runs:/abc123/model",
                    inference_type="text",
                )
                assert predictor.inference_type_override == InferenceType.TEXT

                # Test with InferenceType enum
                predictor = AutoModelPredictor(
                    name="test-model",
                    model_uri="runs:/abc123/model",
                    inference_type=InferenceType.IMAGE,
                )
                assert predictor.inference_type_override == InferenceType.IMAGE

    def test_predict_unified_text(self, predictor):
        """Test unified format with text input."""
        request = {"inputs": {"text": "Hello, world!"}}

        predictor.model.predict.return_value = pd.DataFrame(
            {"predictions": ["positive"], "confidence": [0.95]}
        )

        result = predictor.predict(request)

        assert result["status"] == 200
        assert result["data"]["predictions"] == "positive"
        assert result["data"]["confidence"] == 0.95
        assert result["metadata"]["inference_type"] == "text"

        # Verify DataFrame passed to model
        call_args = predictor.model.predict.call_args[0][0]
        assert isinstance(call_args, pd.DataFrame)
        assert "text" in call_args.columns
        assert call_args.at[0, "text"] == "Hello, world!"

    def test_predict_unified_byte_stream(self, predictor):
        """Test unified format with byte stream input."""
        # Clear output columns to allow all columns
        predictor.model_metadata.outputs = []

        pdf_bytes = b"PDF content here"
        request = {"inputs": {"byte_stream": pdf_bytes, "page_numbers": [1, 2, 3]}}

        predictor.model.predict.return_value = pd.DataFrame(
            {
                "prediction_page_level": ['{"page1": "text1", "page2": "text2"}'],
                "prediction_aggregated": ['{"total": 100}'],
            }
        )

        result = predictor.predict(request)

        assert result["status"] == 200
        assert "prediction_page_level" in result["data"]
        assert "prediction_aggregated" in result["data"]
        assert result["metadata"]["inference_type"] == "byte_stream"

        # Verify DataFrame structure
        call_args = predictor.model.predict.call_args[0][0]
        assert "data" in call_args.columns
        assert "page_numbers" in call_args.columns
        assert call_args.at[0, "data"] == pdf_bytes
        assert call_args.at[0, "page_numbers"] == [1, 2, 3]

    def test_predict_unified_image_base64(self, predictor):
        """Test unified format with base64 images."""
        request = {"inputs": {"image_base64": ["img1_b64", "img2_b64", "img3_b64"]}}

        predictor.model.predict.return_value = pd.DataFrame(
            {"predictions": [[0.1, 0.2, 0.7], [0.8, 0.1, 0.1], [0.3, 0.3, 0.4]]}
        )

        result = predictor.predict(request)

        assert result["status"] == 200
        assert len(result["data"]["predictions"]) == 3
        assert result["metadata"]["inference_type"] == "image_base64"

        # Verify DataFrame has multiple rows
        call_args = predictor.model.predict.call_args[0][0]
        assert len(call_args) == 3
        assert call_args.at[0, "data"] == "img1_b64"
        assert call_args.at[2, "data"] == "img3_b64"

    def test_predict_unified_ocr_text(self, predictor):
        """Test unified format with OCR text."""
        request = {
            "inputs": {
                "ocr_text_list": ["Page 1 text", "Page 2 text"],
                "page_number_list": [1, 2],
            }
        }

        predictor.model.predict.return_value = pd.DataFrame(
            {"predictions": ["extracted info 1", "extracted info 2"]}
        )

        result = predictor.predict(request)

        assert result["status"] == 200
        assert result["metadata"]["inference_type"] == "ocr_text"

        # Verify DataFrame structure
        call_args = predictor.model.predict.call_args[0][0]
        assert len(call_args) == 2
        assert "ocr_text" in call_args.columns
        assert "page_number" in call_args.columns
        assert call_args.at[0, "ocr_text"] == "Page 1 text"
        assert call_args.at[1, "page_number"] == 2

    def test_predict_unified_structured(self, predictor):
        """Test unified format with structured data."""
        # Clear output columns to allow all columns
        predictor.model_metadata.outputs = []

        request = {
            "inputs": {
                "hcpcs_code": "J1234",
                "rate": 150.50,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "provider_id": "P12345",
            }
        }

        predictor.model.predict.return_value = pd.DataFrame(
            {
                "approved": [True],
                "adjusted_rate": [145.00],
                "notes": ["Rate adjusted per contract"],
            }
        )

        result = predictor.predict(request)

        assert result["status"] == 200
        assert result["data"]["approved"]
        assert result["data"]["adjusted_rate"] == 145.00
        assert result["metadata"]["inference_type"] == "structured"

        # Verify all fields passed to model
        call_args = predictor.model.predict.call_args[0][0]
        assert call_args.at[0, "hcpcs_code"] == "J1234"
        assert call_args.at[0, "rate"] == 150.50

    def test_predict_unified_tabular(self, predictor):
        """Test unified format with tabular data."""
        request = {
            "inputs": {
                "data": [
                    {"feature1": 1.0, "feature2": 2.0},
                    {"feature1": 3.0, "feature2": 4.0},
                ]
            }
        }

        predictor.model.predict.return_value = [0.1, 0.9]

        result = predictor.predict(request)

        assert result["status"] == 200
        assert result["data"]["predictions"] == [0.1, 0.9]
        assert result["metadata"]["inference_type"] == "tabular"

        # Verify DataFrame structure
        call_args = predictor.model.predict.call_args[0][0]
        assert len(call_args) == 2
        assert call_args.at[0, "feature1"] == 1.0
        assert call_args.at[1, "feature2"] == 4.0

    def test_predict_with_inference_type_override(self, predictor):
        """Test prediction with explicit inference type."""
        # Override detector to force text processing
        predictor.inference_type_override = InferenceType.TEXT
        predictor.model_metadata.outputs = []

        request = {"inputs": {"data": "This looks like tabular but treat as text"}}

        predictor.model.predict.return_value = pd.DataFrame({"result": ["text result"]})

        result = predictor.predict(request)

        # Should be processed as text despite having "data" field
        assert result["metadata"]["inference_type"] == "text"

        # Verify DataFrame has text column
        call_args = predictor.model.predict.call_args[0][0]
        assert "text" in call_args.columns

    def test_predict_with_request_inference_type(self, predictor):
        """Test prediction with inference type in request."""
        predictor.model_metadata.outputs = []

        request = {"inputs": {"data": "some data"}, "inference_type": "text"}

        predictor.model.predict.return_value = pd.DataFrame(
            {"result": ["processed as text"]}
        )

        result = predictor.predict(request)

        assert result["metadata"]["inference_type"] == "text"

        # Verify text processing was used
        call_args = predictor.model.predict.call_args[0][0]
        assert "text" in call_args.columns

    def test_predict_with_parameters(self, predictor):
        """Test prediction with additional parameters."""
        request = {
            "inputs": {
                "text": "Process this",
                "parameters": {"temperature": 0.7, "max_length": 100},
            }
        }

        predictor.model.predict.return_value = "result"

        result = predictor.predict(request)

        assert result["status"] == 200
        assert result["metadata"]["parameters"] == {
            "temperature": 0.7,
            "max_length": 100,
        }

    def test_predict_v2_mixed_with_unified(self, predictor):
        """Test that V2 protocol is properly detected."""
        # V2 protocol request (with list inputs)
        v2_request = {
            "inputs": [
                {
                    "name": "input",
                    "shape": [1, 3],
                    "datatype": "FP32",
                    "data": [1.0, 2.0, 3.0],
                }
            ]
        }

        predictor.model.predict.return_value = np.array([0.5])

        result = predictor.predict(v2_request)

        # Should be handled by V2 protocol path
        assert "outputs" in result
        assert isinstance(result["outputs"], list)

        # Unified request (with dict inputs)
        unified_request = {"inputs": {"text": "hello"}}

        predictor.model.predict.return_value = "response"

        result = predictor.predict(unified_request)

        # Should be handled by unified path
        assert "data" in result
        assert "metadata" in result

    def test_predict_raw_fallback(self, predictor):
        """Test fallback to raw processing."""
        request = {"inputs": {"custom_field": "value", "another_field": 123}}

        predictor.model.predict.return_value = {"result": "processed"}

        result = predictor.predict(request)

        assert result["status"] == 200
        assert result["metadata"]["inference_type"] == "raw"

        # Verify all fields passed through
        call_args = predictor.model.predict.call_args[0][0]
        assert call_args.at[0, "custom_field"] == "value"
        assert call_args.at[0, "another_field"] == 123

    def test_predict_with_model_metadata_columns(self, predictor):
        """Test that model metadata output columns are used."""
        predictor.model_metadata.outputs = [
            {"name": "prediction_page_level"},
            {"name": "confidence_scores"},
        ]

        request = {"inputs": {"text": "test"}}

        # Model returns more columns than specified in metadata
        predictor.model.predict.return_value = pd.DataFrame(
            {
                "prediction_page_level": ['{"page": 1}'],
                "confidence_scores": [0.95],
                "internal_column": ["should be filtered"],
            }
        )

        result = predictor.predict(request)

        # Only metadata columns should be included
        assert "prediction_page_level" in result["data"]
        assert "confidence_scores" in result["data"]
        assert "internal_column" not in result["data"]

    def test_predict_error_handling_unified(self, predictor):
        """Test error handling in unified prediction."""
        request = {"inputs": {"text": "cause error"}}

        predictor.model.predict.side_effect = RuntimeError("Model failed")

        result = predictor.predict(request)

        assert result["status"] == 400
        assert "Model failed" in result["error"]

    def test_predict_complex_output_transformation(self, predictor):
        """Test complex output transformations."""
        predictor.model_metadata.outputs = []

        request = {"inputs": {"text": "test"}}

        # Test with nested JSON in DataFrame
        predictor.model.predict.return_value = pd.DataFrame(
            {
                "predictions": ['{"classes": ["A", "B"], "scores": [0.7, 0.3]}'],
                "metadata": ['{"processed_at": "2024-01-01", "model": "v1"}'],
            }
        )

        result = predictor.predict(request)

        assert result["status"] == 200
        assert result["data"]["predictions"]["classes"] == ["A", "B"]
        assert result["data"]["predictions"]["scores"] == [0.7, 0.3]
        assert result["data"]["metadata"]["model"] == "v1"

    def test_predict_numpy_output(self, predictor):
        """Test numpy array output handling."""
        request = {"inputs": {"data": [[1, 2], [3, 4]]}}

        predictor.model.predict.return_value = np.array([[0.1, 0.9], [0.8, 0.2]])

        result = predictor.predict(request)

        assert result["status"] == 200
        assert result["data"]["predictions"] == [[0.1, 0.9], [0.8, 0.2]]

    def test_predict_legacy_format_compatibility(self, predictor):
        """Test backward compatibility with legacy format."""
        # Legacy format (no "inputs" key)
        legacy_request = {"text": "This is legacy format"}

        predictor.model.predict.return_value = "legacy result"

        result = predictor.predict(legacy_request)

        assert result["status"] == 200
        assert result["metadata"]["inference_type"] == "text"


class TestAutoModelPredictorIntegration:
    """Integration tests for complete workflows."""

    @pytest.fixture
    def predictor(self):
        """Create predictor for integration tests."""
        with patch("modelhub.serving.base.ModelhubCredential"):
            with patch("modelhub.serving.base.MLflowClient"):
                predictor = AutoModelPredictor(
                    name="test-model", model_uri="runs:/abc123/model"
                )
                predictor.ready = True
                predictor.model_metadata = MagicMock()
                predictor.model_metadata.outputs = []
                return predictor

    def test_pdf_extraction_workflow(self, predictor):
        """Test complete PDF extraction workflow."""

        # Simulate a real PDF extraction model
        def mock_pdf_model(df):
            # Model expects data column
            assert "data" in df.columns

            # Return extraction results
            return pd.DataFrame(
                {
                    "prediction_page_level": [
                        json.dumps(
                            {
                                "page_1": {
                                    "patient_name": "John Doe",
                                    "date_of_service": "2024-01-15",
                                },
                                "page_2": {
                                    "diagnosis": "Type 2 Diabetes",
                                    "procedures": ["A1C Test", "Glucose Test"],
                                },
                            }
                        )
                    ],
                    "prediction_aggregated": [
                        json.dumps(
                            {
                                "total_pages": 2,
                                "document_type": "Medical Record",
                                "confidence": 0.95,
                            }
                        )
                    ],
                }
            )

        predictor.model = Mock()
        predictor.model.predict = mock_pdf_model

        # Send PDF for processing
        request = {
            "inputs": {
                "byte_stream": b"PDF binary content here",
                "page_numbers": [1, 2],
            }
        }

        result = predictor.predict(request)

        assert result["status"] == 200
        assert (
            result["data"]["prediction_page_level"]["page_1"]["patient_name"]
            == "John Doe"
        )
        assert (
            result["data"]["prediction_aggregated"]["document_type"] == "Medical Record"
        )
        assert result["metadata"]["inference_type"] == "byte_stream"

    def test_image_classification_batch_workflow(self, predictor):
        """Test batch image classification workflow."""

        def mock_image_model(df):
            # Model expects data column (containing image_base64 data)
            assert "data" in df.columns
            assert len(df) == 3  # 3 images

            # Return classification for each image
            return pd.DataFrame(
                {
                    "predictions": [
                        json.dumps({"class": "cat", "confidence": 0.95}),
                        json.dumps({"class": "dog", "confidence": 0.87}),
                        json.dumps({"class": "bird", "confidence": 0.92}),
                    ]
                }
            )

        predictor.model = Mock()
        predictor.model.predict = mock_image_model

        request = {
            "inputs": {
                "image_base64": ["cat_image_b64", "dog_image_b64", "bird_image_b64"]
            }
        }

        result = predictor.predict(request)

        assert result["status"] == 200
        # Should return list of predictions for batch
        assert isinstance(result["data"]["predictions"], list)
        assert len(result["data"]["predictions"]) == 3
        assert result["data"]["predictions"][0]["class"] == "cat"
        assert result["data"]["predictions"][1]["confidence"] == 0.87

    def test_medical_billing_workflow(self, predictor):
        """Test medical billing code validation workflow."""

        def mock_billing_model(df):
            # Model expects structured billing data
            assert "hcpcs_code" in df.columns
            assert "rate" in df.columns

            # Validate and adjust rates
            hcpcs = df.at[0, "hcpcs_code"]
            rate = df.at[0, "rate"]

            # Simple business logic
            if hcpcs.startswith("J"):  # Drug codes
                max_rate = 200.00
                approved = rate <= max_rate
                adjusted_rate = min(rate, max_rate)
            else:
                approved = True
                adjusted_rate = rate

            return pd.DataFrame(
                {
                    "approved": [approved],
                    "adjusted_rate": [adjusted_rate],
                    "reason": [
                        "Rate limit applied" if not approved else "Within limits"
                    ],
                    "processed_date": ["2024-01-20"],
                }
            )

        predictor.model = Mock()
        predictor.model.predict = mock_billing_model

        request = {
            "inputs": {
                "hcpcs_code": "J1234",
                "rate": 250.00,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "provider_npi": "1234567890",
            }
        }

        result = predictor.predict(request)

        assert result["status"] == 200
        assert not result["data"]["approved"]
        assert result["data"]["adjusted_rate"] == 200.00
        assert "Rate limit applied" in result["data"]["reason"]
        assert result["metadata"]["inference_type"] == "structured"
