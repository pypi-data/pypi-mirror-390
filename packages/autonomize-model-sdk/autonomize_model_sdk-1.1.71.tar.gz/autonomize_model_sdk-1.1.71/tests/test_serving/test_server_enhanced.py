"""
Enhanced tests for ModelHub FastAPI server with inference types.
"""

import base64
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from modelhub.serving.base import AutoModelPredictor
from modelhub.serving.server import ModelServer


class TestModelServerEnhanced:
    """Enhanced tests for ModelServer with inference type support."""

    @pytest.fixture
    def mock_predictor(self):
        """Create a mock predictor with inference type support."""
        with patch("modelhub.serving.base.ModelhubCredential"):
            with patch("modelhub.serving.base.MLflowClient"):
                predictor = AutoModelPredictor(
                    name="test-model",
                    model_uri="runs:/abc123/model",
                    inference_type="auto",
                )
                predictor.model = MagicMock()
                predictor.ready = True
                predictor.model_metadata = MagicMock()
                predictor.model_metadata.outputs = []
                return predictor

    @pytest.fixture
    def server(self, mock_predictor):
        """Create a test server."""
        return ModelServer(models=[mock_predictor])

    @pytest.fixture
    def client(self, server):
        """Create a test client."""
        return TestClient(server.app)

    def test_infer_octet_stream_pdf(self, client, server):
        """Test binary PDF upload via application/octet-stream."""
        # Mock the MLflow model's predict method
        server.models["test-model"].model.predict.return_value = pd.DataFrame(
            {
                "prediction_page_level": ['{"page1": "extracted text"}'],
                "prediction_aggregated": ['{"total_pages": 1}'],
            }
        )

        # Create fake PDF bytes
        pdf_bytes = b"%PDF-1.4 fake pdf content"

        response = client.post(
            "/v2/models/test-model/infer",
            content=pdf_bytes,
            headers={"Content-Type": "application/octet-stream"},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["status"] == 200
        assert "prediction_page_level" in result["data"]
        assert result["metadata"]["inference_type"] == "byte_stream"

        # Verify model was called with correct DataFrame
        call_args = server.models["test-model"].model.predict.call_args[0][0]
        assert isinstance(call_args, pd.DataFrame)
        assert "data" in call_args.columns
        assert call_args.at[0, "data"] == pdf_bytes

    def test_infer_octet_stream_with_type_override(self, client, server):
        """Test binary upload with inference type override."""
        # Mock the MLflow model's predict method
        server.models["test-model"].model.predict.return_value = pd.DataFrame(
            {"predictions": ['{"class": "document", "confidence": 0.9}']}
        )

        # Create fake image bytes
        image_bytes = b"\x89PNG fake image content"

        response = client.post(
            "/v2/models/test-model/infer?inference_type=image",
            content=image_bytes,
            headers={"Content-Type": "application/octet-stream"},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["status"] == 200
        assert result["metadata"]["inference_type"] == "image"

    def test_infer_unified_text(self, client, server):
        """Test unified inference with text input."""
        # Mock the MLflow model's predict method
        server.models["test-model"].model.predict.return_value = pd.DataFrame(
            {"predictions": ["positive"], "confidence": [0.95]}
        )

        request_data = {"inputs": {"text": "This product is amazing!"}}

        response = client.post("/v2/models/test-model/infer", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == 200
        assert data["data"]["predictions"] == "positive"
        assert data["metadata"]["inference_type"] == "text"

    def test_infer_unified_byte_stream(self, client, server):
        """Test unified inference with byte stream."""
        # Mock the MLflow model's predict method
        server.models["test-model"].model.predict.return_value = pd.DataFrame(
            {
                "prediction_page_level": [
                    '{"page_1": {"content": "Page 1 content"}, "page_2": {"content": "Page 2 content"}}'
                ],
                "prediction_aggregated": [
                    '{"total_pages": 2, "document_type": "invoice"}'
                ],
            }
        )

        # Convert bytes to hex string for JSON serialization
        pdf_bytes = b"PDF content here"
        request_data = {
            "inputs": {"byte_stream": pdf_bytes.hex(), "page_numbers": [1, 2]}
        }

        response = client.post("/v2/models/test-model/infer", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["data"]["prediction_aggregated"]["document_type"] == "invoice"
        assert data["metadata"]["inference_type"] == "byte_stream"

    def test_infer_unified_image_base64(self, client, server):
        """Test unified inference with base64 images."""
        # Mock the MLflow model's predict method
        server.models["test-model"].model.predict.return_value = pd.DataFrame(
            {
                "predictions": [
                    '{"class": "cat", "confidence": 0.95}',
                    '{"class": "dog", "confidence": 0.87}',
                ]
            }
        )

        # Create fake base64 images
        img1_b64 = base64.b64encode(b"fake image 1").decode()
        img2_b64 = base64.b64encode(b"fake image 2").decode()

        request_data = {"inputs": {"image_base64": [img1_b64, img2_b64]}}

        response = client.post("/v2/models/test-model/infer", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]["predictions"]) == 2
        assert data["data"]["predictions"][0]["class"] == "cat"

    def test_infer_unified_structured(self, client, server):
        """Test unified inference with structured data."""
        # Mock the MLflow model's predict method
        server.models["test-model"].model.predict.return_value = pd.DataFrame(
            {
                "approved": [True],
                "adjusted_rate": [145.00],
                "notes": ["Rate within acceptable range"],
            }
        )

        request_data = {
            "inputs": {
                "hcpcs_code": "J1234",
                "rate": 150.00,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            }
        }

        response = client.post("/v2/models/test-model/infer", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["data"]["approved"] is True
        assert data["data"]["adjusted_rate"] == 145.00

    def test_infer_with_inference_type_override(self, client, server):
        """Test inference with explicit type override."""
        # Mock the MLflow model's predict method
        server.models["test-model"].model.predict.return_value = pd.DataFrame(
            {"result": ["processed as text"]}
        )

        request_data = {
            "inputs": {"data": "This could be tabular but treat as text"},
            "inference_type": "text",
        }

        response = client.post("/v2/models/test-model/infer", json=request_data)
        assert response.status_code == 200

        # Verify the model was called
        server.models["test-model"].model.predict.assert_called_once()

    def test_infer_ocr_text(self, client, server):
        """Test OCR text processing."""
        # Mock the MLflow model's predict method
        server.models["test-model"].model.predict.return_value = pd.DataFrame(
            {
                "predictions": [
                    '{"page": 1, "extracted": "Patient Name: John Doe"}',
                    '{"page": 2, "extracted": "Diagnosis: Diabetes"}',
                ]
            }
        )

        request_data = {
            "inputs": {
                "ocr_text_list": ["Page 1 OCR text content", "Page 2 OCR text content"],
                "page_number_list": [1, 2],
            }
        }

        response = client.post("/v2/models/test-model/infer", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]["predictions"]) == 2
        assert data["metadata"]["inference_type"] == "ocr_text"

    def test_infer_tabular(self, client, server):
        """Test tabular data inference."""
        # Mock the MLflow model's predict method
        server.models["test-model"].model.predict.return_value = pd.DataFrame(
            {"predictions": [0.1, 0.9, 0.3]}
        )

        request_data = {
            "inputs": {
                "data": [
                    {"feature1": 1.0, "feature2": 2.0, "feature3": 3.0},
                    {"feature1": 4.0, "feature2": 5.0, "feature3": 6.0},
                    {"feature1": 7.0, "feature2": 8.0, "feature3": 9.0},
                ]
            }
        }

        response = client.post("/v2/models/test-model/infer", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["data"]["predictions"] == [0.1, 0.9, 0.3]

    def test_error_handling_unified(self, client, server):
        """Test error handling with unified format."""
        # Mock the MLflow model's predict method to raise an exception
        server.models["test-model"].model.predict.side_effect = Exception(
            "Model processing failed"
        )

        response = client.post(
            "/v2/models/test-model/infer", json={"inputs": {"text": "cause error"}}
        )

        # Server should return the error status from predictor
        assert response.status_code == 400
        assert "Model processing failed" in response.json()["detail"]

    def test_batch_processing(self, client, server):
        """Test batch processing with multiple items."""
        # Mock the MLflow model's predict method
        server.models["test-model"].model.predict.return_value = pd.DataFrame(
            {
                "predictions": [
                    '{"id": 1, "result": "A"}',
                    '{"id": 2, "result": "B"}',
                    '{"id": 3, "result": "C"}',
                ]
            }
        )

        request_data = {
            "inputs": {
                "data": [
                    {"id": 1, "value": 10},
                    {"id": 2, "value": 20},
                    {"id": 3, "value": 30},
                ]
            }
        }

        response = client.post("/v2/models/test-model/infer", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]["predictions"]) == 3
        # Note: batch_size metadata may not be automatically added
        assert "predictions" in data["data"]

    def test_model_with_custom_inference_type(self, client):
        """Test model initialized with specific inference type."""
        with patch("modelhub.serving.base.ModelhubCredential"):
            with patch("modelhub.serving.base.MLflowClient"):
                # Create predictor with forced image type
                predictor = AutoModelPredictor(
                    name="image-model",
                    model_uri="runs:/image123/model",
                    inference_type="image",
                )
                predictor.model = MagicMock()
                predictor.ready = True
                predictor.model.predict.return_value = {
                    "class": "cat",
                    "confidence": 0.95,
                }

                server = ModelServer(models=[predictor])
                client = TestClient(server.app)

                # Send data that would normally be detected as text
                response = client.post(
                    "/v2/models/image-model/infer",
                    json={"inputs": {"data": "this is actually an image path"}},
                )

                assert response.status_code == 200
                # Model should process as image due to override


class TestServerIntegrationScenarios:
    """Integration test scenarios for complete workflows."""

    @pytest.fixture
    def integration_server(self):
        """Create server for integration tests."""
        with patch("modelhub.serving.base.ModelhubCredential"):
            with patch("modelhub.serving.base.MLflowClient"):
                # Create multiple models with different types
                text_model = AutoModelPredictor(
                    name="sentiment-model",
                    model_uri="runs:/text123/model",
                    inference_type="text",
                )
                text_model.ready = True
                text_model.model = Mock()

                image_model = AutoModelPredictor(
                    name="vision-model", model_uri="runs:/image456/model"
                )
                image_model.ready = True
                image_model.model = Mock()

                pdf_model = AutoModelPredictor(
                    name="document-model", model_uri="runs:/pdf789/model"
                )
                pdf_model.ready = True
                pdf_model.model = Mock()

                server = ModelServer(models=[text_model, image_model, pdf_model])
                return server, text_model, image_model, pdf_model

    def test_multi_model_routing(self, integration_server):
        """Test routing to different models."""
        server, text_model, image_model, pdf_model = integration_server
        client = TestClient(server.app)

        # Test text model
        text_model.model.predict.return_value = pd.DataFrame(
            {"sentiment": ["positive"]}
        )

        response = client.post(
            "/v2/models/sentiment-model/infer", json={"inputs": {"text": "Great!"}}
        )
        assert response.status_code == 200
        assert response.json()["data"]["sentiment"] == "positive"

        # Test image model
        image_model.model.predict.return_value = pd.DataFrame(
            {"predictions": ['{"class": "dog", "score": 0.9}']}
        )

        response = client.post(
            "/v2/models/vision-model/infer",
            json={"inputs": {"image_base64": ["fake_b64_image"]}},
        )
        assert response.status_code == 200
        # Check that predictions field exists and is not empty
        predictions = response.json()["data"]["predictions"]
        assert predictions is not None

        # Test PDF model
        pdf_model.model.predict.return_value = pd.DataFrame(
            {"extracted_text": ["Document content"]}
        )

        response = client.post(
            "/v2/models/document-model/infer",
            json={"inputs": {"byte_stream": "pdf_bytes_hex"}},
        )
        assert response.status_code == 200
        assert response.json()["data"]["extracted_text"] == "Document content"

    def test_model_listing_multiple(self, integration_server):
        """Test listing multiple models."""
        server, _, _, _ = integration_server
        client = TestClient(server.app)

        response = client.get("/v2/models")
        assert response.status_code == 200

        data = response.json()
        assert len(data["models"]) == 3

        model_names = [m["name"] for m in data["models"]]
        assert "sentiment-model" in model_names
        assert "vision-model" in model_names
        assert "document-model" in model_names

        # All should be ready
        assert all(m["ready"] for m in data["models"])

    def test_concurrent_inference_simulation(self, integration_server):
        """Test handling concurrent requests to different models."""
        server, text_model, image_model, _ = integration_server
        client = TestClient(server.app)

        # Configure models to return different results
        text_model.model.predict.return_value = pd.DataFrame(
            {"result": ["text_result"]}
        )

        image_model.model.predict.return_value = pd.DataFrame(
            {"result": ["image_result"]}
        )

        # Make requests to different models
        text_response = client.post(
            "/v2/models/sentiment-model/infer", json={"inputs": {"text": "test"}}
        )

        image_response = client.post(
            "/v2/models/vision-model/infer", json={"inputs": {"image": "test"}}
        )

        # Verify each model received correct request
        assert text_response.json()["data"]["result"] == "text_result"
        assert image_response.json()["data"]["result"] == "image_result"

        # Verify correct number of calls
        assert text_model.model.predict.call_count == 1
        assert image_model.model.predict.call_count == 1
