# Fix for inference_client.py tests
from unittest.mock import MagicMock

import httpx
import pytest

from modelhub.clients.inference_client import InferenceClient
from modelhub.core import ModelhubCredential


@pytest.fixture
def mock_credential():
    """Create a mock ModelhubCredential."""
    credential = MagicMock(spec=ModelhubCredential)
    credential.get_token.return_value = "dummy-token"
    credential._modelhub_url = "http://example.com"
    return credential


@pytest.fixture
def inference_client(mock_credential):
    """Create a test inference client with proper mocking."""
    client = InferenceClient(
        credential=mock_credential,
        client_id="1",
    )
    # Mock the httpx client to prevent actual HTTP requests
    client.client = MagicMock()
    client.async_client = MagicMock()
    return client


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(self, status_code, json_data=None, content=None, headers=None):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.content = content or b""
        self.headers = headers or {}
        self.text = str(content) if content else ""
        self.url = "http://example.com/test"

    def json(self):
        """Return JSON data."""
        return self._json_data

    def raise_for_status(self):
        """Raise for status like httpx."""
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("Error", request=None, response=self)


def test_run_file_inference_url_success(monkeypatch, inference_client):
    """Test successful file inference with a URL."""
    # Mock the URL download
    mock_get_response = MockResponse(
        200, content=b"fake image data from url", headers={"Content-Type": "image/png"}
    )

    # Mock httpx.get globally to avoid actual HTTP requests
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: mock_get_response)

    # Set up inference response
    response_data = {
        "result": {"objects": [{"class": "cat", "confidence": 0.92}]},
        "processing_time": 0.321,
    }

    # Mock the post method at the BaseClient level
    monkeypatch.setattr(inference_client, "post", lambda *args, **kwargs: response_data)

    # Call the function
    result = inference_client.run_file_inference(
        model_name="image-model", file_path="https://example.com/images/cat.png"
    )

    # Check the result
    assert result == response_data


def test_run_file_inference_signed_url_success(monkeypatch, inference_client):
    """Test successful file inference with a signed URL."""
    # Mock the URL download
    signed_url = (
        "https://storage.example.com/bucket/object.pdf?signature=abc123&expiry=123456"
    )
    mock_get_response = MockResponse(
        200,
        content=b"fake pdf data from signed url",
        headers={"Content-Type": "application/pdf"},
    )

    # Mock httpx.get globally
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: mock_get_response)

    # Set up inference response
    response_data = {
        "result": {"text": "Extracted PDF text"},
        "processing_time": 0.654,
    }

    # Mock the post method
    monkeypatch.setattr(inference_client, "post", lambda *args, **kwargs: response_data)

    # Call the function with explicit filename and content type
    result = inference_client.run_file_inference(
        model_name="pdf-model",
        file_path=signed_url,
        file_name="document.pdf",
        content_type="application/pdf",
    )

    # Check the result
    assert result == response_data


def test_run_file_inference_url_extraction_fallback(monkeypatch, inference_client):
    """Test URL with no extractable filename falls back to default."""
    # Mock the URL download
    mock_get_response = MockResponse(
        200, content=b"fake data", headers={"Content-Type": "image/jpeg"}
    )

    # Mock httpx.get globally
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: mock_get_response)

    # Set up response for inference post
    response_data = {"result": {}}
    monkeypatch.setattr(inference_client, "post", lambda *args, **kwargs: response_data)

    # Mock os.path.basename to return empty string to test fallback
    monkeypatch.setattr("os.path.basename", lambda path: "")

    # Call the function
    result = inference_client.run_file_inference(
        model_name="image-model", file_path="https://example.com/"
    )

    # Check the result
    assert result == response_data


def test_file_inference_with_mock_session(monkeypatch, inference_client, tmp_path):
    """Test file inference using full session mocking."""
    # Create a test file
    file_path = tmp_path / "test.jpg"
    file_path.write_bytes(b"test image data")

    # Configure mock response
    response_data = {"result": "success"}

    # Mock the post method
    monkeypatch.setattr(inference_client, "post", lambda *args, **kwargs: response_data)

    # Test the function
    result = inference_client.run_file_inference("model", str(file_path))

    # Verify result
    assert result == response_data


def test_inference_client_integration(monkeypatch, inference_client):
    """Test with a mocked client to ensure proper integration."""
    # Mock the _process_file method to avoid actual file processing
    monkeypatch.setattr(
        inference_client,
        "_process_file",
        lambda *args, **kwargs: ("test.jpg", b"fake data", "image/jpeg"),
    )

    # Mock the post response
    response_data = {"result": "success"}
    monkeypatch.setattr(inference_client, "post", lambda *args, **kwargs: response_data)

    # Execute the test
    result = inference_client.run_file_inference("test-model", "dummy_path")

    # Verify results
    assert result == response_data
