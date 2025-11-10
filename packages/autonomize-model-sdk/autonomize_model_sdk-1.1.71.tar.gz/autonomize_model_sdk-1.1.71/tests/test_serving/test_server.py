"""Tests for ModelHub FastAPI server."""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from modelhub.serving.base import AutoModelPredictor
from modelhub.serving.server import ModelServer, create_server_from_env


class TestModelServer:
    """Test ModelServer class."""

    @pytest.fixture
    def mock_predictor(self):
        """Create a mock predictor."""
        with patch("modelhub.serving.base.ModelhubCredential"):
            with patch("modelhub.serving.base.MLflowClient"):
                predictor = AutoModelPredictor(
                    name="test-model", model_uri="runs:/abc123/model"
                )
                predictor.model = MagicMock()
                predictor.ready = True
                return predictor

    @pytest.fixture
    def server(self, mock_predictor):
        """Create a test server."""
        server = ModelServer(models=[mock_predictor])
        return server

    @pytest.fixture
    def client(self, server):
        """Create a test client."""
        return TestClient(server.app)

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "ModelHub Inference Server"
        assert data["protocol"] == "v2"

    def test_health_live(self, client):
        """Test live health check."""
        response = client.get("/v2/health/live")
        assert response.status_code == 200
        assert response.json()["live"] is True

    def test_health_ready(self, client):
        """Test ready health check."""
        response = client.get("/v2/health/ready")
        assert response.status_code == 200
        assert response.json()["ready"] is True

    def test_health_ready_not_loaded(self, client, server):
        """Test ready health check when models not loaded."""
        # Set model to not ready
        server.models["test-model"].ready = False

        response = client.get("/v2/health/ready")
        assert response.status_code == 503
        assert "not ready" in response.json()["detail"]

    def test_list_models(self, client):
        """Test list models endpoint."""
        response = client.get("/v2/models")
        assert response.status_code == 200

        data = response.json()
        assert "models" in data
        assert len(data["models"]) == 1
        assert data["models"][0]["name"] == "test-model"
        assert data["models"][0]["ready"] is True

    def test_model_metadata(self, client, server):
        """Test model metadata endpoint."""
        # Mock get_model_metadata method
        server.models["test-model"].get_model_metadata = MagicMock(
            return_value={
                "name": "test-model",
                "platform": "mlflow",
                "inputs": [{"name": "input", "datatype": "FP32", "shape": [-1]}],
            }
        )

        response = client.get("/v2/models/test-model")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "test-model"
        assert data["platform"] == "mlflow"
        assert len(data["inputs"]) == 1

    def test_model_metadata_not_found(self, client):
        """Test model metadata for non-existent model."""
        response = client.get("/v2/models/unknown-model")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_model_ready(self, client):
        """Test model ready endpoint."""
        response = client.get("/v2/models/test-model/ready")
        assert response.status_code == 200
        assert response.json()["ready"] is True
        assert response.json()["name"] == "test-model"

    def test_model_ready_not_found(self, client):
        """Test model ready for non-existent model."""
        response = client.get("/v2/models/unknown-model/ready")
        assert response.status_code == 404

    def test_model_ready_not_loaded(self, client, server):
        """Test model ready when not loaded."""
        server.models["test-model"].ready = False

        response = client.get("/v2/models/test-model/ready")
        assert response.status_code == 503

    def test_infer_v2(self, client, server):
        """Test V2 inference endpoint."""
        # Mock predict method
        server.models["test-model"].predict = MagicMock(
            return_value={
                "model_name": "test-model",
                "outputs": [
                    {"name": "output", "shape": [1], "datatype": "FP32", "data": [0.95]}
                ],
            }
        )

        request_data = {
            "inputs": [
                {
                    "name": "input",
                    "shape": [1, 3],
                    "datatype": "FP32",
                    "data": [1.0, 2.0, 3.0],
                }
            ]
        }

        response = client.post("/v2/models/test-model/infer", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["model_name"] == "test-model"
        assert len(data["outputs"]) == 1
        assert data["outputs"][0]["data"] == [0.95]

    def test_infer_model_not_found(self, client):
        """Test inference with non-existent model."""
        response = client.post("/v2/models/unknown-model/infer", json={})
        assert response.status_code == 404

    def test_infer_model_not_ready(self, client, server):
        """Test inference when model not ready."""
        server.models["test-model"].ready = False

        response = client.post("/v2/models/test-model/infer", json={})
        assert response.status_code == 503

    def test_infer_error(self, client, server):
        """Test inference error handling."""
        server.models["test-model"].predict = MagicMock(
            side_effect=ValueError("Test error")
        )

        response = client.post("/v2/models/test-model/infer", json={"inputs": []})
        assert response.status_code == 400
        assert "Test error" in response.json()["detail"]

    def test_add_model(self, server):
        """Test adding a model to server."""
        with patch("modelhub.serving.base.ModelhubCredential"):
            with patch("modelhub.serving.base.MLflowClient"):
                new_model = AutoModelPredictor(
                    name="new-model", model_uri="runs:/xyz789/model"
                )

                server.add_model(new_model)

                assert "new-model" in server.models
                assert server.models["new-model"] == new_model


class TestCreateServerFromEnv:
    """Test server creation from environment variables."""

    def test_single_model_with_uri(self):
        """Test creating server with single model URI."""
        env_vars = {"MODEL_NAME": "my-model", "MODEL_URI": "runs:/abc123/model"}

        with patch.dict(os.environ, env_vars):
            with patch("modelhub.serving.base.ModelhubCredential"):
                with patch("modelhub.serving.base.MLflowClient"):
                    server = create_server_from_env()

                    assert len(server.models) == 1
                    assert "my-model" in server.models
                    model = server.models["my-model"]
                    assert model.model_uri == "runs:/abc123/model"

    def test_single_model_with_registry(self):
        """Test creating server with model registry."""
        env_vars = {
            "MODEL_NAME": "my-model",
            "MODEL_NAME_REGISTRY": "registered-model",
            "MODEL_VERSION": "3",
        }

        with patch.dict(os.environ, env_vars):
            with patch("modelhub.serving.base.ModelhubCredential"):
                with patch("modelhub.serving.base.MLflowClient"):
                    server = create_server_from_env()

                    assert len(server.models) == 1
                    model = server.models["my-model"]
                    assert model.model_name == "registered-model"
                    assert model.model_version == "3"

    def test_multiple_models(self):
        """Test creating server with multiple models."""
        env_vars = {
            "MODEL_NAME_1": "model-1",
            "MODEL_URI_1": "runs:/abc123/model",
            "MODEL_NAME_2": "model-2",
            "MODEL_NAME_REGISTRY_2": "registered-model",
            "MODEL_VERSION_2": "2",
        }

        with patch.dict(os.environ, env_vars):
            with patch("modelhub.serving.base.ModelhubCredential"):
                with patch("modelhub.serving.base.MLflowClient"):
                    server = create_server_from_env()

                    assert len(server.models) == 2
                    assert "model-1" in server.models
                    assert "model-2" in server.models

                    assert server.models["model-1"].model_uri == "runs:/abc123/model"
                    assert server.models["model-2"].model_name == "registered-model"

    def test_no_models_configured(self):
        """Test error when no models configured."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="No models configured"):
                create_server_from_env()

    def test_default_model_name(self):
        """Test default model name when not specified."""
        env_vars = {"MODEL_URI": "runs:/abc123/model"}

        with patch.dict(os.environ, env_vars):
            with patch("modelhub.serving.base.ModelhubCredential"):
                with patch("modelhub.serving.base.MLflowClient"):
                    server = create_server_from_env()

                    assert "default-model" in server.models
