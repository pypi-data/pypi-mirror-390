from unittest.mock import MagicMock, patch

import pytest

from modelhub.clients import DatasetClient, MLflowClient
from modelhub.core import BaseClient


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to set up environment variables for testing."""
    monkeypatch.setenv("MODELHUB_BASE_URL", "https://test-api.example.com")
    monkeypatch.setenv("MODELHUB_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("MODELHUB_CLIENT_SECRET", "test-client-secret")


@pytest.fixture
def mock_auth_token():
    """Mock successful auth token response."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "token": {"access_token": "test-token"}
        }
        yield mock_post


@pytest.fixture
def mock_successful_response():
    """Fixture to create a mock successful response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "key": "value",
            "versions": ["v1", "v2"],
            "signedUrl": "https://test-signed-url.com",
            "id": "test-id",
        }
    }
    return mock_response


@pytest.fixture
def base_client(mock_env_vars, mock_auth_token):
    """Fixture to create a BaseClient instance with mocked auth."""
    return BaseClient()


@pytest.fixture
def mlflow_client(mock_env_vars, mock_auth_token):
    """Fixture to create a MLflowClient instance with mocked auth."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "tracking_uri": "test-uri",
            "username": "test-user",
            "password": "test-pass",
        }
        return MLflowClient()


@pytest.fixture
def dataset_client(mock_env_vars, mock_auth_token):
    """Fixture to create a DatasetClient instance with mocked auth."""
    return DatasetClient()


@pytest.fixture
def prompt_client(mock_env_vars, mock_auth_token):
    """Fixture to create a PromptClient instance with mocked auth."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "tracking_uri": "test-uri",
            "username": "test-user",
            "password": "test-pass",
        }
        return PromptClient()
