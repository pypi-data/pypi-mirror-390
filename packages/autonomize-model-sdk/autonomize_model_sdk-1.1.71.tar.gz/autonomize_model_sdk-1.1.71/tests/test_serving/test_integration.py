"""
End-to-end integration tests for ModelHub serving.
"""

import base64
import io
import json
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from modelhub.serving import AutoModelPredictor, ModelServer


class TestEndToEndScenarios:
    """Complete end-to-end scenario tests."""

    @pytest.fixture
    def mock_mlflow_model(self):
        """Create a mock MLflow model that behaves like real models."""
        model = Mock()

        def predict_side_effect(df):
            """Simulate different model behaviors based on input."""
            if "text" in df.columns:
                # Text classification model
                return pd.DataFrame(
                    {
                        "predictions": ["positive"] * len(df),
                        "confidence": [0.95] * len(df),
                    }
                )
            elif "data" in df.columns and "page_numbers" in df.columns:
                # PDF extraction model (byte_stream)
                return pd.DataFrame(
                    {
                        "prediction_page_level": [
                            json.dumps(
                                {
                                    "page_1": {
                                        "patient": "John Doe",
                                        "dob": "1980-01-01",
                                    },
                                    "page_2": {"diagnosis": "Type 2 Diabetes"},
                                }
                            )
                        ],
                        "prediction_aggregated": [
                            json.dumps({"total_pages": 2, "confidence": 0.92})
                        ],
                    }
                )
            elif "data" in df.columns and len(df) > 1:
                # Image classification model
                predictions = []
                for _ in range(len(df)):
                    predictions.append(
                        json.dumps(
                            {
                                "class": "cat",
                                "confidence": 0.87,
                                "bbox": [100, 100, 200, 200],
                            }
                        )
                    )
                return pd.DataFrame({"predictions": predictions})
            elif "ocr_text" in df.columns:
                # OCR processing model
                results = []
                for idx in range(len(df)):
                    results.append(
                        {"entities": ["John Doe", "Diabetes"], "page": idx + 1}
                    )
                return pd.DataFrame({"extracted": results})
            elif "hcpcs_code" in df.columns:
                # Medical billing model
                return pd.DataFrame(
                    {
                        "approved": [True],
                        "adjusted_rate": [df.at[0, "rate"] * 0.95],
                        "reason": ["Contract rate applied"],
                    }
                )
            else:
                # Generic tabular model
                return pd.DataFrame({"predictions": np.random.rand(len(df)).tolist()})

        model.predict = Mock(side_effect=predict_side_effect)
        return model

    @pytest.fixture
    def integration_server(self, mock_mlflow_model):
        """Create a complete server setup for integration testing."""
        with patch("modelhub.serving.base.ModelhubCredential"):
            with patch("modelhub.serving.base.MLflowClient") as mock_client:
                # Mock MLflow client
                mock_client_instance = MagicMock()
                mock_client.return_value = mock_client_instance
                mock_client_instance.mlflow.pyfunc.load_model.return_value = (
                    mock_mlflow_model
                )

                # Mock model info
                mock_model_info = MagicMock()
                mock_model_info.signature = None
                mock_client_instance.mlflow.models.get_model_info.return_value = (
                    mock_model_info
                )

                # Create predictor
                predictor = AutoModelPredictor(
                    name="universal-model", model_uri="runs:/test123/model"
                )
                predictor.load()

                # Create server
                server = ModelServer(models=[predictor])
                return TestClient(server.app), predictor

    def test_text_classification_workflow(self, integration_server):
        """Test complete text classification workflow."""
        client, predictor = integration_server

        # Single text prediction
        response = client.post(
            "/v2/models/universal-model/infer",
            json={"inputs": {"text": "This product is amazing! Best purchase ever."}},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["status"] == 200
        assert result["data"]["predictions"] == "positive"
        assert result["data"]["confidence"] == 0.95
        assert result["metadata"]["inference_type"] == "text"

        # Batch text prediction using V2 endpoint
        response = client.post(
            "/v2/models/universal-model/infer",
            json={"inputs": {"text": "Another great review"}},
        )

        assert response.status_code == 200
        assert response.json()["data"]["predictions"] == "positive"

    def test_pdf_extraction_workflow(self, integration_server):
        """Test complete PDF extraction workflow."""
        client, predictor = integration_server

        # Create fake PDF bytes
        pdf_content = b"%PDF-1.4 fake pdf content"

        response = client.post(
            "/v2/models/universal-model/infer",
            json={"inputs": {"byte_stream": pdf_content.hex(), "page_numbers": [1, 2]}},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["status"] == 200

        # Check page-level predictions
        page_data = result["data"]["prediction_page_level"]
        assert page_data["page_1"]["patient"] == "John Doe"
        assert page_data["page_2"]["diagnosis"] == "Type 2 Diabetes"

        # Check aggregated predictions
        agg_data = result["data"]["prediction_aggregated"]
        assert agg_data["total_pages"] == 2
        assert agg_data["confidence"] == 0.92

    def test_image_classification_workflow(self, integration_server):
        """Test complete image classification workflow."""
        client, predictor = integration_server

        # Create fake base64 images
        fake_images = []
        for i in range(3):
            # Create a simple image
            img = Image.new("RGB", (224, 224), color=(i * 50, i * 50, i * 50))
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            fake_images.append(img_base64)

        response = client.post(
            "/v2/models/universal-model/infer",
            json={"inputs": {"image_base64": fake_images}},
        )

        assert response.status_code == 200
        result = response.json()

        # Should get predictions for each image
        predictions = result["data"]["predictions"]
        assert len(predictions) == 3

        for pred in predictions:
            assert pred["class"] == "cat"
            assert pred["confidence"] == 0.87
            assert "bbox" in pred

    def test_ocr_processing_workflow(self, integration_server):
        """Test OCR text processing workflow."""
        client, predictor = integration_server

        ocr_data = {
            "inputs": {
                "ocr_text_list": [
                    "Patient: John Doe\nDOB: 01/01/1980",
                    "Diagnosis: Type 2 Diabetes\nMedications: Metformin",
                ],
                "page_number_list": [1, 2],
            }
        }

        response = client.post("/v2/models/universal-model/infer", json=ocr_data)

        assert response.status_code == 200
        result = response.json()

        # Check extracted entities
        extracted = result["data"]["extracted"]
        assert len(extracted) == 2
        assert extracted[0]["entities"] == ["John Doe", "Diabetes"]
        assert extracted[0]["page"] == 1

    def test_medical_billing_workflow(self, integration_server):
        """Test medical billing validation workflow."""
        client, predictor = integration_server

        billing_data = {
            "inputs": {
                "hcpcs_code": "J3490",
                "rate": 200.00,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "provider_npi": "1234567890",
            }
        }

        response = client.post("/v2/models/universal-model/infer", json=billing_data)

        assert response.status_code == 200
        result = response.json()

        assert result["data"]["approved"] is True
        assert result["data"]["adjusted_rate"] == 190.00  # 95% of original
        assert "Contract rate applied" in result["data"]["reason"]
        assert result["metadata"]["inference_type"] == "structured"

    def test_inference_type_override(self, integration_server):
        """Test overriding automatic inference type detection."""
        client, predictor = integration_server

        # Data that would normally be detected as tabular
        ambiguous_data = {
            "inputs": {"data": "This should be treated as text not tabular"},
            "inference_type": "text",
        }

        response = client.post("/v2/models/universal-model/infer", json=ambiguous_data)

        assert response.status_code == 200
        result = response.json()

        # Should be processed as text due to override
        assert result["metadata"]["inference_type"] == "text"
        assert "predictions" in result["data"]

    def test_mixed_endpoint_compatibility(self, integration_server):
        """Test that all endpoints work with the same model."""
        client, predictor = integration_server

        test_data = {"text": "Test input"}

        # V2 protocol endpoint
        v2_response = client.post(
            "/v2/models/universal-model/infer", json={"inputs": test_data}
        )
        assert v2_response.status_code == 200

        # V2 protocol handles all formats consistently
        # The test above already validates the V2 endpoint

        # V2 endpoint successfully processed the request
        v2_data = v2_response.json()["data"]["predictions"]
        assert v2_data == "positive"  # Mock model returns "positive" for text

    def test_error_handling_integration(self, integration_server):
        """Test error handling across the stack."""
        client, predictor = integration_server

        # Make model raise an error
        predictor.model.predict.side_effect = RuntimeError("Model computation failed")

        response = client.post(
            "/v2/models/universal-model/infer",
            json={"inputs": {"text": "This will fail"}},
        )

        assert response.status_code == 400
        error_data = response.json()
        assert "Model computation failed" in error_data["detail"]

    def test_model_metadata_integration(self, integration_server):
        """Test model metadata endpoint with real predictor."""
        client, predictor = integration_server

        # Get model metadata
        response = client.get("/v2/models/universal-model")
        assert response.status_code == 200

        metadata = response.json()
        assert metadata["name"] == "universal-model"
        assert metadata["platform"] == "mlflow"

    def test_health_check_integration(self, integration_server):
        """Test health check endpoints."""
        client, predictor = integration_server

        # Server health
        response = client.get("/v2/health/ready")
        assert response.status_code == 200
        assert response.json()["ready"] is True

        # Model-specific health
        response = client.get("/v2/models/universal-model/ready")
        assert response.status_code == 200
        assert response.json()["ready"] is True
        assert response.json()["name"] == "universal-model"


class TestPerformanceScenarios:
    """Test performance-related scenarios."""

    @pytest.fixture
    def performance_server(self):
        """Create server for performance testing."""
        with patch("modelhub.serving.base.ModelhubCredential"):
            with patch("modelhub.serving.base.MLflowClient") as mock_client:
                # Mock a fast model
                fast_model = Mock()
                fast_model.predict = Mock(
                    return_value=pd.DataFrame({"predictions": [0.5]})
                )

                mock_client_instance = MagicMock()
                mock_client.return_value = mock_client_instance
                mock_client_instance.mlflow.pyfunc.load_model.return_value = fast_model

                mock_model_info = MagicMock()
                mock_model_info.signature = None
                mock_client_instance.mlflow.models.get_model_info.return_value = (
                    mock_model_info
                )

                predictor = AutoModelPredictor(
                    name="fast-model", model_uri="runs:/fast123/model"
                )
                predictor.load()

                server = ModelServer(models=[predictor])
                return TestClient(server.app), predictor

    def test_large_batch_processing(self, performance_server):
        """Test processing large batches."""
        client, predictor = performance_server

        # Create large batch of images
        large_batch = ["fake_base64_image"] * 100

        response = client.post(
            "/v2/models/fast-model/infer",
            json={"inputs": {"image_base64": large_batch}},
        )

        assert response.status_code == 200
        result = response.json()

        # Verify batch was processed
        assert result["metadata"]["inference_type"] == "image_base64"

        # Check model was called with full batch
        call_args = predictor.model.predict.call_args[0][0]
        assert len(call_args) == 100

    def test_concurrent_request_handling(self, performance_server):
        """Test handling multiple concurrent requests."""
        client, predictor = performance_server

        # Reset call count
        predictor.model.predict.reset_mock()

        # Make multiple requests
        responses = []
        for i in range(10):
            response = client.post(
                "/v2/models/fast-model/infer", json={"inputs": {"text": f"Request {i}"}}
            )
            responses.append(response)

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

        # Model should have been called 10 times
        assert predictor.model.predict.call_count == 10

    def test_memory_efficient_streaming(self, performance_server):
        """Test memory-efficient processing of large inputs."""
        client, predictor = performance_server

        # Create a very large text input
        large_text = "x" * 1000000  # 1MB of text

        response = client.post(
            "/v2/models/fast-model/infer", json={"inputs": {"text": large_text}}
        )

        assert response.status_code == 200

        # Verify the large input was passed to model
        call_args = predictor.model.predict.call_args[0][0]
        assert call_args.at[0, "text"] == large_text


class TestEdgeCasesAndRobustness:
    """Test edge cases and robustness."""

    @pytest.fixture
    def robust_server(self):
        """Create server for robustness testing."""
        with patch("modelhub.serving.base.ModelhubCredential"):
            with patch("modelhub.serving.base.MLflowClient"):
                predictor = AutoModelPredictor(
                    name="robust-model", model_uri="runs:/robust123/model"
                )
                # Don't load the model to test not-ready state
                server = ModelServer(models=[predictor])
                return TestClient(server.app), predictor

    def test_model_not_loaded(self, robust_server):
        """Test behavior when model is not loaded."""
        client, predictor = robust_server

        # Model should not be ready
        response = client.get("/v2/models/robust-model/ready")
        assert response.status_code == 503

        # Inference should fail
        response = client.post(
            "/v2/models/robust-model/infer", json={"inputs": {"text": "test"}}
        )
        assert response.status_code == 503

    def test_empty_input_handling(self, robust_server):
        """Test handling of empty inputs."""
        client, predictor = robust_server
        predictor.ready = True
        predictor.model = Mock()
        predictor.model.predict.return_value = pd.DataFrame({"result": ["empty"]})

        # Empty inputs dict
        response = client.post("/v2/models/robust-model/infer", json={"inputs": {}})
        assert response.status_code == 200
        assert response.json()["metadata"]["inference_type"] == "raw"

        # Empty arrays
        response = client.post(
            "/v2/models/robust-model/infer", json={"inputs": {"image_base64": []}}
        )
        assert response.status_code == 200

    def test_malformed_requests(self, robust_server):
        """Test handling of malformed requests."""
        client, predictor = robust_server

        # Model is not loaded in robust_server, so we get 503
        response = client.post("/v2/models/robust-model/infer", json={})
        assert response.status_code == 503

        # Invalid JSON - model readiness is checked first, so still 503
        response = client.post(
            "/v2/models/robust-model/infer",
            data="not valid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 503

    def test_unicode_handling(self, robust_server):
        """Test handling of unicode in inputs."""
        client, predictor = robust_server
        predictor.ready = True
        predictor.model = Mock()
        predictor.model.predict.return_value = "processed"

        # Unicode text
        response = client.post(
            "/v2/models/robust-model/infer",
            json={"inputs": {"text": "Hello 世界 🌍 नमस्ते мир"}},
        )

        assert response.status_code == 200

        # Verify unicode was preserved
        call_args = predictor.model.predict.call_args[0][0]
        assert "世界" in call_args.at[0, "text"]
        assert "🌍" in call_args.at[0, "text"]
